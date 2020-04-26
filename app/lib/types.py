from dataclasses import dataclass
from typing import Any, Dict, Callable, TYPE_CHECKING

from telegram import Update
from telegram.ext import CallbackContext

if TYPE_CHECKING:
    from app.models import User


@dataclass(frozen=True)
class TelegramCtx:
    context: CallbackContext
    user: 'User'


DataDict = Dict[str, Any]


TelegramCallback = Callable[[Update, CallbackContext], Any]
UserTelegramCallback = Callable[[Update, TelegramCtx], Any]

