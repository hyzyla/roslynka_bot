import random
from functools import wraps
from typing import Any, Optional

import telegram
from flask import request
from telegram import Update
from telegram.ext import CallbackContext

from app import db, dispatcher
from app.lib.errors import BaseError
from app.lib.types import UserTelegramCallback, TelegramCallback, TelegramCtx
from app.lib.utils import reply_message
from app.models import TelegramUser, User


def generate_name() -> str:
    return f'Рослинка {random.randint(0, 1000)}'


def select_telegram_user(user_id: str) -> TelegramUser:
    return (
        db.session.query(TelegramUser)
        .join(TelegramUser.user)
        .filter(TelegramUser.id == user_id)
        .first()
    )


def get_user_from_update(update: Update) -> User:
    from_user = update.effective_user

    telegram_user_id: str = from_user.id
    telegram_user = select_telegram_user(telegram_user_id)

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

    return telegram_user.user


def telegram_callback(func: UserTelegramCallback) -> TelegramCallback:
    return user_required(error_reply(func))


def callback_answer(func: UserTelegramCallback) -> UserTelegramCallback:
    @wraps(func)
    def wrapped(update: Update, ctx: TelegramCtx) -> Any:
        if update.callback_query:
            update.callback_query.answer()
        return func(update, ctx)

    return wrapped


def error_reply(func: UserTelegramCallback) -> UserTelegramCallback:
    """ Catch all errors raised in telegram callback and reply with error message """
    @wraps(func)
    def wrapped(update: Update, ctx: TelegramCtx) -> Any:
        try:
            return func(update, ctx)
        except BaseError as error:
            reply_message(update, error.text)

    return wrapped


def user_required(func: UserTelegramCallback) -> TelegramCallback:
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext) -> Any:
        user = get_user_from_update(update)
        ctx = TelegramCtx(context=context, user=user)
        return func(update, ctx)

    return wrapped


def get_update_from_request():
    bot = dispatcher.bot
    return telegram.Update.de_json(request.get_json(force=True), bot)


def get_photo_id_update(update: Update) -> Optional[str]:
    message = update.message
    photos = message.photo
    if not photos:
        return None
    biggest = photos[0]
    for photo in photos:
        if photo.file_size > biggest.file_size:
            biggest = photo

    return biggest.file_id


