import logging
import os
from queue import Queue

import telegram
from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from telegram import Update
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


def command_start(update: Update, context):
    print("START COMMAND")
    update.message.reply_text("Hello")


dispatcher.add_handler(CommandHandler('start', command_start))


@app.route('/', methods=['GET', 'POST'])
def bot_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'

import tables

if __name__ == '__main__':
    app.run()
