from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from get_google_service import get_google_service

# update keyboard
def keyboard(activities):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for activity in activities:
        keyboard.add(InlineKeyboardButton(text=activity, callback_data=f"status_{activity}"))

    # add cancel button
    keyboard.add(InlineKeyboardButton(text="EXIT", callback_data="CANCEL"))

    return keyboard

# display all activities for user to update
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
    bot.reply_to(message, "Choose an activity", reply_markup = keyboard(activities))

# selected activity to update
def select_activity(bot, callback):
    # ensure the correct user that interact with the button
    if callback.message.reply_to_message.from_user.id != callback.from_user.id:
        return
    
    # get the activity name from the callback query
    activity = callback.data.split("_")[1]

    markup = InlineKeyboardMarkup(row_width=2)
    yes = InlineKeyboardButton('Yes', callback_data=f'update_{activity}_yes')
    no = InlineKeyboardButton('No', callback_data=f'update_{activity}_no')
    markup.add(yes, no)

    bot.send_message(callback.message.chat.id, text=f"{activity} completed?", reply_markup=markup)

# callback update activity
def update_activity(bot, callback):
    # ensure the correct user that interact with the button
    if callback.json['from']['id'] != callback.from_user.id:
        return
    
    # get google sheet service
    try:
        sheet = get_google_service()
    except:
        bot.reply_to(callback, "Error: Cannot connect to Google Sheet")
        return

    # get the activity name from the callback query
    activity = callback.data.split("_")[1]
    wks = sheet.worksheet(str(callback.from_user.username))
    cell = wks.find(activity.lower())

    if cell is None:
        return

    status = callback.data.split("_")[2]
    if status == 'yes':
        wks.update_cell(cell.row, 2, str(True))
    elif status == 'no':
        wks.update_cell(cell.row, 2, str(False))

    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{activity} has been updated")