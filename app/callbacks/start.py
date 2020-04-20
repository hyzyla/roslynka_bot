from telegram import Update

from app.lib.types import TelegramCtx
from app.utils import telegram_callback


@telegram_callback
def on_start_command(update: Update, _: TelegramCtx) -> None:
    update.message.reply_text(f"Привіт!")

