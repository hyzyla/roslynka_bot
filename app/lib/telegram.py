from typing import Optional, Tuple, Any

from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler

from app.lib.types import TelegramCallback


class CallbackHandler(CallbackQueryHandler):
    def __init__(self, type_: str, callback: TelegramCallback, ) -> None:
        self.type_ = type_
        super().__init__(callback)

    def check_update(self, update: Update) -> bool:
        if not (isinstance(update, Update) and update.callback_query):
            return False

        data = update.callback_query.data
        parts = data.split('|')
        if not parts:
            return False
        return parts[0] == self.type_


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


