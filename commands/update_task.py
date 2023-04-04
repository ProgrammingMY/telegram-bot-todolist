from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from get_google_service import get_google_service

status_map = {
    "true": "🟢",
    "false": "🔴"
}

# update keyboard
def keyboard(activities):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for activity in activities:
        status = status_map[str(activity['done']).lower()]
        keyboard.add(InlineKeyboardButton(text=f"{status} {activity['activity']}", callback_data=f"status_{activity['activity']}"))

    # add cancel button
    keyboard.add(InlineKeyboardButton(text="EXIT", callback_data="CANCEL"))

    return keyboard

# display all activities for user to update
def display_activity(bot, collection, message):
    # get id
    id = message.from_user.id
    
    # get all activities
    activities = collection.find({"user": id})
    bot.reply_to(message, "Choose an activity to update its status", reply_markup = keyboard(activities))

# selected activity to update
def select_activity(bot, collection, callback):
    # ensure the correct user that interact with the button
    if callback.message.reply_to_message.from_user.id != callback.from_user.id:
        return
    
    # get id
    id = callback.from_user.id

    # get the activity name from the callback query
    activity = callback.data.split("_")[1]

    # update activity
    query = {"user": id, "activity": activity}
    update = {"$set": {"done": not collection.find_one(query)['done']}}

    result = collection.update_one(query, update)
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Choose an activity to update its status", reply_markup=keyboard(collection.find({"user": id})))

    