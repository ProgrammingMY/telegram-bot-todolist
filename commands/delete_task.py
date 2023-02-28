# delete task
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from get_google_service import get_google_service

# contruct inline keyboard button
def keyboard(activities):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for activity in activities:
        button = InlineKeyboardButton(activity, callback_data=f"delete_{activity}")
        keyboard.add(button)

    button = InlineKeyboardButton("EXIT", callback_data="CANCEL")
    keyboard.add(button)

    return keyboard

# delete task function
def display_activity(bot, message):
     # get username
    username = str(message.from_user.username)

    # get google sheet service
    try:
        sheet = get_google_service()
    except:
        bot.reply_to(message, "Error: Cannot connect to Google Sheet")
        return

    # check if the sheet is available for user
    try:
        wks = sheet.worksheet(username)
    except:
        wks = sheet.add_worksheet(username, rows=100, cols=5)
        wks.update('A1', 'Activity')
        wks.update('B1', 'Done')
    
    # get all activities
    activities = wks.col_values(1)[1:]
    bot.reply_to(message, "Delete which activity?", reply_markup = keyboard(activities))

# delete task
def delete_activity(bot, callback):
    # ensure the correct user that interact with the button
    if callback.message.reply_to_message.from_user.id != callback.from_user.id:
        return
    
    # get the task name from the callback query
    activity = callback.data.split("_")[1]

    # get google sheet service
    try:
        sheet = get_google_service()
    except:
        bot.reply_to(callback.message.chat.id, "Error: Cannot connect to Google Sheet")
        return
    
    # delete activity
    wks = sheet.worksheet(str(callback.from_user.username))
    cell = wks.find(activity)

    # The activity is not found
    if cell is None:
        bot.send_message(callback.message.chat.id, "The activity is not found")
        return
    
    wks.delete_rows(cell.row)

    # update the list
    activities = wks.col_values(1)[1:]
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Delete which activity?", reply_markup=keyboard(activities))
    bot.send_message(callback.message.chat.id, activity + " has been deleted")