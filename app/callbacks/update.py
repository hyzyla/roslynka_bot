from datetime import timedelta

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, Filters, MessageHandler

from app import db
from app.callbacks.list import on_list_button
from app.lib.telegram import InlineButton, CallbackHandler
from app.lib.types import TelegramCtx
from app.lib.utils import update_message, reply_message
from app.models import Plant
from app.utils import get_photo_id_update, telegram_callback

UPDATE_NAME_STATE = 'UPDATE_NAME'
UPDATE_INTERVAL_STATE = 'UPDATE_INTERVAL_STATE'
UPDATE_PHOTO_STATE = 'UPDATE_PHOTO_STATE'


def plant_description(plant: Plant):
    return (
        f'*{plant.name}*\n'
        f'Потрібно поливати кожні {plant.watering_interval.days} днів'
    )


def get_callback_plant_id(update: Update) -> str:
    _, plant_id = update.callback_query.data.split('|')
    return plant_id


def get_context_plant_id(ctx: TelegramCtx) -> str:
    return ctx.context.user_data['plant_id']


def get_callback_plant(update: Update) -> Plant:
    plant_id = get_callback_plant_id(update)
    return Plant.query.get(plant_id)


def get_context_plant(ctx: TelegramCtx) -> Plant:
    plant_id = get_context_plant_id(ctx)
    return Plant.query.get(plant_id)


def plant_photo_button(plant: Plant):
    if plant.photo_id:
        text = 'Фото'
        data = ('plant-photo', plant.id)
    else:
        text = 'Додати фото'
        data = ('plant-update-photo', plant.id)
    return InlineButton(text=text, data=data)


def get_plant_keyboard(plant: Plant) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [plant_photo_button(plant)],
        [InlineButton(text="Оновити ім’я", data=('plant-name', plant.id))],
        [InlineButton(text="Оновити інтервал", data=('plant-interval', plant.id))],
        [InlineButton(text="Видалити", data=('plant-delete', plant.id))],
        [InlineButton(text="Нагадування", data=('plant-notification', plant.id))],
        [InlineButton(text='Всі рослинки', data=('plant-menu',))]
    ])


def update_plant_screen(update: Update, plant: Plant) -> None:
    keyboard = get_plant_keyboard(plant)
    update_message(
        update=update,
        text=plant_description(plant),
        keyboard=keyboard,
    )


def send_plant_screen(update: Update, plant: Plant) -> None:
    keyboard = get_plant_keyboard(plant)
    reply_message(
        update=update,
        text=plant_description(plant),
        keyboard=keyboard,
    )


@telegram_callback
def on_name_button(update: Update, ctx: TelegramCtx):

    plant_id = get_callback_plant_id(update)

    ctx.context.user_data['plant_id'] = plant_id

    reply_message(update, "Введіть нове ім’я")
    return UPDATE_NAME_STATE


@telegram_callback
def on_name_reply(update: Update, ctx: TelegramCtx):

    plant = get_context_plant(ctx)
    plant.name = update.message.text  # TODO: add validation
    db.session.commit()

    send_plant_screen(update, plant)

    return ConversationHandler.END


@telegram_callback
def on_interval_button(update: Update, ctx: TelegramCtx):

    plant_id = get_callback_plant_id(update)
    ctx.context.user_data['plant_id'] = plant_id
    reply_message(update, "Введіть новий інтервал")
    return UPDATE_INTERVAL_STATE


@telegram_callback
def on_interval_reply(update: Update, ctx: TelegramCtx):
    plant_id = get_context_plant_id(ctx)

    plant = Plant.query.get(plant_id)
    plant.watering_interval = timedelta(days=int(update.message.text))
    db.session.commit()

    send_plant_screen(update, plant)
    return ConversationHandler.END


@telegram_callback
def on_show_photo_button(update: Update, _: TelegramCtx):
    update.effective_message.delete()

    plant = get_callback_plant(update)

    keyboard = InlineKeyboardMarkup([[
        InlineButton(text='Оновити фото', data=('plant-update-photo', plant.id)),
        InlineButton(text='Назад', data=('plant-choose', plant.id))
    ]])

    update.effective_user.send_photo(
        photo=plant.photo_id,
        reply_markup=keyboard,
    )


@telegram_callback
def on_update_photo_button(update: Update, ctx: TelegramCtx):

    plant_id = get_callback_plant_id(update)
    ctx.context.user_data['plant_id'] = plant_id

    reply_message(update, "Надішліть фото")

    return UPDATE_PHOTO_STATE


@telegram_callback
def on_photo_reply(update: Update, ctx: TelegramCtx):

    photo_id = get_photo_id_update(update)

    plant = get_context_plant(ctx)
    plant.photo_id = photo_id
    db.session.commit()

    send_plant_screen(update, plant)
    return ConversationHandler.END


@telegram_callback
def on_delete_button(update: Update, ctx: TelegramCtx):
    plant = get_callback_plant(update)

    db.session.delete(plant)
    db.session.commit()

    on_list_button(update, ctx)


@telegram_callback
def on_plant_button(update: Update, _: TelegramCtx):
    plant = get_callback_plant(update)
    update_plant_screen(update, plant)


@telegram_callback
def on_photo_back_button(update: Update, _: TelegramCtx):
    plant = get_callback_plant(update)
    send_plant_screen(update, plant)


def get_name_conversation() -> ConversationHandler:
    # Update plant name
    return ConversationHandler(
        entry_points=[CallbackHandler('plant-name', on_name_button)],
        states={
            UPDATE_NAME_STATE: [MessageHandler(Filters.text, on_name_reply)],
        },
        fallbacks=[],
    )


def get_interval_conversation() -> ConversationHandler:
    # Update plant time interval
    return ConversationHandler(
        entry_points=[CallbackHandler('plant-interval', on_interval_button)],
        states={
            UPDATE_INTERVAL_STATE: [
                MessageHandler(Filters.regex(r'^\d+$'), on_interval_reply),
                MessageHandler(Filters.text, on_interval_reply),
            ],
        },
        fallbacks=[],
    )


def get_photo_conversation() -> ConversationHandler:
    # Update plant photo
    return ConversationHandler(
        entry_points=[CallbackHandler('plant-update-photo', on_update_photo_button)],
        states={
            UPDATE_PHOTO_STATE: [MessageHandler(Filters.photo, on_photo_reply)],
        },
        fallbacks=[],
    )
