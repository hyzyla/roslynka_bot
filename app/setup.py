import logging
import os
from queue import Queue

import telegram
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from telegram.ext import CommandHandler as Command, Dispatcher

from app.lib.telegram import CallbackHandler as Callback


def prepare_logging() -> None:
    logging.basicConfig(level='DEBUG')


def prepare_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['TELEGRAM_TOKEN'] = os.getenv('TELEGRAM_TOKEN')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app


def prepare_db(app: Flask) -> SQLAlchemy:
    return SQLAlchemy(app)


def prepare_migration(app: Flask, db: SQLAlchemy) -> Migrate:
    return Migrate(app, db)


def prepare_dispatcher(app: Flask) -> Dispatcher:
    bot = telegram.Bot(app.config['TELEGRAM_TOKEN'])
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)

    return dispatcher


def prepare_handlers(dp: Dispatcher) -> None:
    from app.callbacks import add, list, update

    dp.add_handler(Command('list', list.on_list_command))
    dp.add_handler(Callback('plant-choose', update.on_plant_button))
    dp.add_handler(Callback('plant-choose-from-phot', update.on_photo_back_button))
    dp.add_handler(Callback('plant-menu', list.on_list_button))
    dp.add_handler(Callback('plant-photo', update.on_show_photo_button))
    dp.add_handler(Callback('plant-delete', update.on_delete_button))
    dp.add_handler(add.get_conversation())
    dp.add_handler(update.get_interval_conversation())
    dp.add_handler(update.get_name_conversation())
    dp.add_handler(update.get_photo_conversation())


