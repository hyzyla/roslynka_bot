from typing import List

from telegram import InlineKeyboardMarkup, Update

from app.lib.telegram import InlineButton
from app.lib.types import TelegramCtx
from app.lib.utils import reply_message, update_message
from app.models import Plant
from app.utils import telegram_callback

Plants = List[Plant]

TEXT = 'Всі твої рослинок:'


def build_keyboard(ctx: TelegramCtx):
    plants: Plants = ctx.user.home.plants
    buttons = [
        [InlineButton(text=plant.name, data=('plant-choose', plant.id))]
        for plant in plants
    ]
    return InlineKeyboardMarkup(buttons)


@telegram_callback
def on_list_command(update: Update, ctx: TelegramCtx) -> None:
    keyboard = build_keyboard(ctx)
    reply_message(update, text=TEXT, keyboard=keyboard)


@telegram_callback
def on_list_button(update: Update, ctx: TelegramCtx) -> None:
    keyboard = build_keyboard(ctx)
    update_message(update, text=TEXT, keyboard=keyboard)


@telegram_callback
def on_list_reply(update: Update, ctx: TelegramCtx) -> None:
    return on_list_command(update, ctx)
