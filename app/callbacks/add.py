import enum
from datetime import timedelta

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from app import db
from app.lib.errors import BadInput
from app.lib.types import TelegramCtx
from app.lib.utils import reply_message
from app.models import Home, User, Plant
from app.utils import generate_name, telegram_callback

ON_ADD_TEXT = 'Додаємо нову квітку. Як часто треба поливати квітку (в днях)'
CHOOSE_NAME_TEXT = "Вкажіть ім'я вашої рослинки"
SKIP_OPTION = 'Пропустити'


@enum.unique
class AddPlantStates(enum.Enum):
    ADDING_INTERVAL = 'ADDING_INTERVAL'
    ADDING_NAME = 'ADDING_NAME'
    END = ConversationHandler.END


def prepare_user_home(user: User):
    home = user.home
    if home:
        return home

    # build new home add to the session
    home = Home()
    user.home = home
    db.session.add(home)


def add_new_plant(update: Update, ctx: TelegramCtx, name: str):

    days = int(ctx.context.user_data['days'])
    home = prepare_user_home(ctx.user)

    watering_interval = timedelta(days=days)
    plant = Plant(name=name, watering_interval=watering_interval, home=home)
    db.session.add(plant)
    db.session.commit()

    reply_message(update, 'TADA!')

    return AddPlantStates.END


@telegram_callback
def on_add_command(update: Update, _: TelegramCtx):
    reply_message(update, ON_ADD_TEXT)
    return AddPlantStates.ADDING_INTERVAL


@telegram_callback
def on_interval_reply(update: Update, ctx: TelegramCtx):

    # TODO: add correct validation
    days = update.effective_message.text
    if days == '0':
        raise BadInput('Має бути числом не рівним 0')

    ctx.context.user_data['days'] = days

    reply_message(
        update=update,
        text=CHOOSE_NAME_TEXT,
        keyborad=ReplyKeyboardMarkup(
            keyboard=[[SKIP_OPTION]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return AddPlantStates.ADDING_NAME


@telegram_callback
def on_bad_interval_reply(update: Update, _: TelegramCtx):
    reply_message(update, "Спробуйте ввести одне число")


@telegram_callback
def on_name_replied(update: Update, ctx: TelegramCtx):
    name = update.message.text  # TODO: add validation
    return add_new_plant(update, ctx, name=name)


@telegram_callback
def on_skip_name_replied(update: Update, ctx: TelegramCtx):
    name = generate_name()
    return add_new_plant(update, ctx, name=name)


def get_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler('add', on_add_command)],
        states={
            AddPlantStates.ADDING_INTERVAL: [
                # Accept only number
                MessageHandler(Filters.regex(r'^\d+$'), on_interval_reply),
                MessageHandler(Filters.all, on_bad_interval_reply)
            ],
            AddPlantStates.ADDING_NAME: [
                MessageHandler(Filters.text([SKIP_OPTION]), on_skip_name_replied),
                MessageHandler(Filters.text, on_name_replied)
            ]
        },
        # TODO: add fallbacks
        fallbacks=[]
    )
