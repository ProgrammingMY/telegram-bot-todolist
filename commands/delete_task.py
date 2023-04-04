# delete task
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from get_google_service import get_google_service

# contruct inline keyboard button
def keyboard(activities):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for activity in activities:
        button = InlineKeyboardButton(activity['activity'], callback_data=f"delete_{activity['activity']}")
        keyboard.add(button)

    button = InlineKeyboardButton("EXIT", callback_data="CANCEL")
    keyboard.add(button)

    return keyboard

# delete task function
def display_activity(bot, collection, message):
    # get id
    id = message.from_user.id
    
    # get all activities
    activities = collection.find({"user": id})
    bot.reply_to(message, "Delete which activity?", reply_markup = keyboard(activities))

# delete task
def delete_activity(bot,collection, callback):
    # ensure the correct user that interact with the button
    if callback.message.reply_to_message.from_user.id != callback.from_user.id:
        return
    
    # get the task name from the callback query
    activity = callback.data.split("_")[1]

    # get user id
    id = callback.from_user.id
    
    # delete activity
    query = {"user": id, "activity": activity}
    result = collection.delete_one(query)

    # The activity is not found
    if result.deleted_count == 0:
        bot.send_message(callback.message.chat.id, "The activity is not found")
        return

    # update the list
    activities = collection.find({"user": id})
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Delete which activity?", reply_markup=keyboard(activities))
    bot.send_message(callback.message.chat.id, activity + " has been deleted")