# def plant_notification(update, plant: Plant):
#     buttons = [
#         [InlineButton(text='Полито', data=('plant-watering', plant.id))],
#     ]
#     reply_markup = InlineKeyboardMarkup(buttons)
#     update.effective_user.send_photo(
#         photo=plant.photo_id,
#         reply_markup=reply_markup,
#     )
#
#
#
#
# @telegram_callback
# def notify_plant(update: Update, ctx: TelegramCtx):
#     _, plant_id = update.callback_query.data.split('|')
#     plant = Plant.query.get(plant_id)
#     plant_notification(update, plant)
#
#
# @telegram_callback
# def watering_plant(update: Update, ctx: TelegramCtx):
#     _, plant_id = update.callback_query.data.split('|')
#
#     watering = PlantWatering(plant_id=plant_id, user_id=telegram_user.user_id)
#     db.session.add(watering)
#     db.session.commit()
#     update.effective_message.edit_reply_markup()
# dispatcher.add_handler(CallbackHandler(notify_plant, type_='plant-notification'))
# dispatcher.add_handler(CallbackHandler(watering_plant, type_='plant-watering'))
