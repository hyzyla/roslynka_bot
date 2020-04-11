import logging
import os
import enum
from queue import Queue

import telegram
from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from telegram import Update
from telegram.ext import (
    CommandHandler, Dispatcher, ConversationHandler, Filters,
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


@app.route('/', methods=['GET', 'POST'])
def bot_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'


from tables import TelegramUser, User


def get_or_create_telegram_user(update: Update) -> TelegramUser:
    from_user = update.message.from_user
    telegram_user_id: str = update.message.from_user.id
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
        db.session.add(telegram_user)
        db.session.commit()

    return telegram_user


def command_start(update: Update, context):
    telegram_user = get_or_create_telegram_user(update)
    print(telegram_user)

    name = telegram_user.first_name or telegram_user.username
    update.message.reply_text(f"Привіт, {name}!")


def command_add(update: Update, context):
    telegram_user = get_or_create_telegram_user(update)
    update.message.reply_text(
        f"Додаємо нову квітку. Як часто треба поливати квітку (в днях)"
    )
    return AddPlantStates.ADDING_INTERVAL


def adding_interval(update: Update, context):
    update.message.reply_text(f"Ваш вибір: {update.message.text}")
    return ConversationHandler.END


@enum.unique
class AddPlantStates(enum.Enum):

    ADDING_INTERVAL = 'ADDING_INTERVAL'


dispatcher.add_handler(CommandHandler('start', command_start))
dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler('add', command_add)],
        states={
            AddPlantStates.ADDING_INTERVAL: [
                MessageHandler(Filters.regex(r'^\d+$'), adding_interval),
            ],
        },
        fallbacks=[]
    )
)

if __name__ == '__main__':
    app.run()
