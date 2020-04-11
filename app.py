import logging
import os
from queue import Queue

import telegram
from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from telegram import Update, Message, User
from telegram.ext import CommandHandler, Dispatcher

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


from tables import TelegramUser


def get_or_create_telegram_user(update: Update) -> TelegramUser:
    message: Message = update.message
    user: User = message.from_user
    telegram_user_id = user.id
    telegram_user = TelegramUser.query.get(telegram_user_id)
    if not telegram_user:
        telegram_user = TelegramUser(
            id=telegram_user_id,
            first_name=user.first_name,
            last_name=user.first_name,
            username=user.first_name,
            language_code=user.language_code,
        )
        db.session.add(telegram_user)
        db.session.add(telegram_user)
        db.session.commit()

    return telegram_user


def command_start(update: Update, context):
    telegram_user = get_or_create_telegram_user(update)
    print(telegram_user, telegram_user.username)
    update.message.reply_text("Hello")


dispatcher.add_handler(CommandHandler('start', command_start))

if __name__ == '__main__':
    app.run()
