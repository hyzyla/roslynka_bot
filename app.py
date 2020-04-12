import enum
import json
import logging
import os
import random
from datetime import timedelta
from functools import wraps
from queue import Queue
from typing import Any, Dict, Optional, Tuple

import telegram
from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
)
from telegram.ext import (
    CallbackQueryHandler, CommandHandler, ConversationHandler, Dispatcher, Filters,
    MessageHandler
)

logging.basicConfig(level='DEBUG')

# app config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['TELEGRAM_TOKEN'] = os.getenv('TELEGRAM_TOKEN')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Bot config
bot = telegram.Bot(app.config['TELEGRAM_TOKEN'])
update_queue = Queue()
dispatcher = Dispatcher(bot, update_queue, use_context=True)

DataDict = Dict[str, Any]


@app.route('/', methods=['GET', 'POST'])
def bot_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'


from tables import TelegramUser, User, Plant, Home


def user_required(func):
    @wraps(func)
    def wrapped(update, context):
        user = get_or_create_telegram_user(update)
        return func(update, context, user)

    return wrapped


def get_or_create_telegram_user(update: Update) -> TelegramUser:
    from_user = update.effective_user
    telegram_user_id: str = from_user.id
    telegram_user = TelegramUser.query.get(telegram_user_id)

    if not telegram_user:
        telegram_user = TelegramUser(
            id=telegram_user_id,
            first_name=from_user.first_name,
            last_name=from_user.first_name,
            username=from_user.first_name,
            language_code=from_user.language_code,
        )
        telegram_user.user = User()

        db.session.add(telegram_user)
        db.session.commit()

    return telegram_user


def generate_name():
    return f'Рослинка {random.randint(0, 1000)}'


def plant_description(plant: Plant):
    return (
        f'*{plant.name}*\n'
        f'Потрібно поливати кожні {plant.watering_interval.days} днів'
    )


def parse_json(data: str) -> DataDict:
    try:
        return json.loads(data)
    except ValueError:
        return {}


def update_message(update: Update, *args, **kwargs):
    if update.callback_query:
        update.effective_message.edit_text(*args, **kwargs)
    else:
        update.effective_message.reply_text(*args, **kwargs)


class InlineButton(InlineKeyboardButton):

    def __init__(
        self,
        text: str,
        data: Optional[Tuple] = None,
        **kwargs: Any,
    ) -> None:
        if data is not None:
            kwargs.setdefault('callback_data', '|'.join(map(str, data)))
        super().__init__(text, **kwargs)


class CallbackHandler(CallbackQueryHandler):
    def __init__(self, callback, type_):
        self.type_ = type_
        super().__init__(callback)

    def check_update(self, update):
        if not (isinstance(update, Update) and update.callback_query):
            return False

        data = update.callback_query.data
        parts = data.split('|')
        if not parts:
            return False
        return parts[0] == self.type_


def plant_screen(update: Update, plant: Plant):
    button_list = [
        [InlineButton(text="Оновити ім’я", data=('plant-name', plant.id))],
        [InlineButton(text="Оновити інтервал", data=('plant-interval', plant.id))],
        [InlineButton(text='Всі рослинки', data=('plant-menu',))]
    ]
    reply_markup = InlineKeyboardMarkup(button_list)
    update_message(
        update=update,
        text=plant_description(plant),
        reply_markup=reply_markup,
        parse_mode='Markdown',
    )


@user_required
def command_start(update: Update, context, telegram_user):
    name = telegram_user.first_name or telegram_user.username
    update.message.reply_text(f"Привіт, {name}!")


@user_required
def command_add(update: Update, context, user):
    update.message.reply_text(
        f"Додаємо нову квітку. Як часто треба поливати квітку (в днях)"
    )
    return AddPlantStates.ADDING_INTERVAL


def adding_interval(update: Update, context):
    menu_keyboard = [['Пропустити']]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True,
                                      resize_keyboard=True)

    days = update.message.text
    context.user_data['days'] = days
    update.message.reply_text(
        f"Ваш вибір: {days}. вкажіть ім'я вашої рослинки",
        reply_markup=menu_markup

    )
    return AddPlantStates.ADDING_NAME


def adding_interval_fallback(update, context):
    update.message.reply_text("Спробуйте ввести одне число")


@user_required
def adding_name(update, context, telegram_user):
    name = update.message.text
    reply_markup = telegram.ReplyKeyboardRemove()
    if name == 'Пропустити':
        name = generate_name()
    days = int(context.user_data['days'])
    home = telegram_user.user.home
    if not home:
        home = Home()
        telegram_user.user.home = home
        db.session.add(home)

    watering_interval = timedelta(days=days)
    plant = Plant(name=name, watering_interval=watering_interval, home=home)
    db.session.add(plant)
    db.session.commit()

    update.message.reply_markdown(
        text=plant_description(plant),
        reply_markup=reply_markup,
    )
    return ConversationHandler.END


@user_required
def command_list(update, context, telegram_user):
    user = telegram_user.user
    plants = user.home.plants
    text = f'Всі твої рослинок:'
    button_list = [
        [InlineButton(text=plant.name, data=('plant-choose', plant.id))]
        for plant in plants
    ]
    reply_markup = InlineKeyboardMarkup(button_list)
    update_message(update, text, reply_markup=reply_markup)


@user_required
def choose_plant(update, context, telegram_user):
    _, plant_id = update.callback_query.data.split('|')
    plant = Plant.query.get(plant_id)

    update.callback_query.answer()
    plant_screen(update, plant)


@user_required
def ask_update_name(update, context, telegram_user):
    _, plant_id = update.callback_query.data.split('|')
    context.user_data['plant_id'] = plant_id
    update.effective_message.edit_text("Введіть нове ім’я")
    return UPDATE_NAME_STATE


@user_required
def update_name(update, context, telegram_user):
    name = update.message.text
    plant_id = context.user_data['plant_id']

    plant = Plant.query.get(plant_id)
    plant.name = name
    db.session.commit()

    plant_screen(update, plant)
    return ConversationHandler.END


@user_required
def ask_update_interval(update, context, telegram_user):
    _, plant_id = update.callback_query.data.split('|')
    context.user_data['plant_id'] = plant_id
    update.effective_message.edit_text("Введіть новий інтервал")
    return UPDATE_INTERVAL_STATE


@user_required
def update_interval(update, context, telegram_user):
    plant_id: str = context.user_data['plant_id']

    plant = Plant.query.get(plant_id)
    plant.watering_interval = timedelta(days=int(update.message.text))
    db.session.commit()

    plant_screen(update, plant)
    return ConversationHandler.END


@enum.unique
class AddPlantStates(enum.Enum):
    ADDING_INTERVAL = 'ADDING_INTERVAL'
    ADDING_NAME = 'ADDING_NAME'


UPDATE_NAME_STATE = 'UPDATE_NAME'
UPDATE_INTERVAL_STATE = 'UPDATE_INTERVAL_STATE'


dispatcher.add_handler(CommandHandler('start', command_start))
dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler('add', command_add)],
        states={
            AddPlantStates.ADDING_INTERVAL: [
                MessageHandler(Filters.regex(r'^\d+$'), adding_interval),
                MessageHandler(Filters.all, adding_interval_fallback)
            ],
            AddPlantStates.ADDING_NAME: [MessageHandler(Filters.text, adding_name)]
        },
        fallbacks=[]
    )
)
# Update plant name
dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CallbackHandler(ask_update_name, type_='plant-name')],
        states={
            UPDATE_NAME_STATE: [MessageHandler(Filters.text, update_name)],
        },
        fallbacks=[],
    )
)
# Update plant time interval
dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CallbackHandler(ask_update_interval, type_='plant-interval')],
        states={
            UPDATE_INTERVAL_STATE: [MessageHandler(Filters.text, update_interval)],
        },
        fallbacks=[],
    )
)

dispatcher.add_handler(CommandHandler('list', command_list))
dispatcher.add_handler(CallbackHandler(choose_plant, type_='plant-choose'))
dispatcher.add_handler(CallbackHandler(command_list, type_='plant-menu'))

if __name__ == '__main__':
    app.run()
