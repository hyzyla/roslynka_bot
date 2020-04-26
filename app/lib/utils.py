import datetime
import json
import uuid
from typing import Any, Optional

from telegram import Update, ReplyMarkup

from app.lib.types import DataDict


def generate_uuid() -> str:
    return str(uuid.uuid4())


def now():
    return datetime.datetime.utcnow()


def parse_json(data: str) -> DataDict:
    try:
        return json.loads(data)
    except ValueError:
        return {}


def update_message(
    update: Update,
    text: str,
    keyboard: Optional[ReplyMarkup] = None,
    **kwargs: Any,
) -> None:
    kwargs.setdefault('parse_mode', 'Markdown')
    update.effective_message.edit_text(text=text, reply_markup=keyboard, **kwargs)


def reply_message(
    update: Update,
    text: str,
    keyboard: Optional[ReplyMarkup] = None,
    **kwargs: Any
) -> None:
    update.effective_message.reply_text(text=text, reply_markup=keyboard, **kwargs)