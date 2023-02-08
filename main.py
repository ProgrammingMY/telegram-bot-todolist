import os
import gspread
import threading
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

## google account credentials
credentials = {
  "type": os.getenv('TYPE'),
  "project_id": os.getenv('PROJECT_ID'),
  "private_key_id": os.getenv('PRIVATE_KEY_ID'),
  "private_key": os.getenv('PRIVATE_KEY').replace('\\n', '\n'),
  "client_email": os.getenv('CLIENT_EMAIL'),
  "client_id": os.getenv('CLIENT_ID'),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.getenv('CLIENT_X509_CERT_URL')
}

acc = gspread.service_account_from_dict(credentials)
sheet = acc.open(os.getenv('SHEET'))
lock = threading.Lock()

# contruct inline keyboard button
def reply_keyboard(activities):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for activity in activities:
        button = InlineKeyboardButton(activity, callback_data=f"delete_{activity}")
        keyboard.add(button)

    button = InlineKeyboardButton("EXIT", callback_data="CANCEL")
    keyboard.add(button)

    return keyboard

def inline_keyboard(items):
    markup = InlineKeyboardMarkup(row_width=1)
    for item in items:
        button = InlineKeyboardButton(item, callback_data=f"status_{item}")
        markup.add(button)

    button = InlineKeyboardButton("EXIT", callback_data="CANCEL")
    markup.add(button)

    return markup

bot = telebot.TeleBot(TOKEN)
print("Bot is online....")

status_map = {
    "true": "🟢",
    "false": "🔴"
}

def construct_table(data, spacing=15):
    spaces = " "
    table = "```\n"
    for row in data:
        repeats = spacing - len(row[0])
        table += row[0] + (spaces*repeats) + status_map[str(row[1]).lower()] + "\n"

    table += " ```"
    return table

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome!\n\
    /start - Getting started\n\
    /add <activity> - Add an activity into list\n\
    /delete - Delete an activity from the list\n\
    /update - Update the status of an activity\n\
    /list - Display all activities and their status", parse_mode="Markdown")

# add a activity
@bot.message_handler(commands=['add'])
def add_activity(message):
    # get argument
    args = message.text.split()[1:]
    if args == []:
        return
    activity = " ".join(args).lower()

    # get username
    username = str(message.from_user.username)

    # check if the sheet is available for user
    try:
        wks = sheet.worksheet(username)
    except:
        wks = sheet.add_worksheet(username, rows=100, cols=5)
        wks.update('A1', 'Activity')
        wks.update('B1', 'Done')

    # find row with the activity
    cell = wks.find(activity)

    if cell is None:
        wks.append_row([activity, str(False)], table_range="A1:B1")
        bot.reply_to(message, "Added")
    else:
        bot.reply_to(message, "The activity already there")

    

# delete a activity
@bot.message_handler(commands=['delete'])
def delete_activity(message):
    # get username
    username = str(message.from_user.username)

    # check if the sheet is available for user
    try:
        wks = sheet.worksheet(username)
    except:
        wks = sheet.add_worksheet(username, rows=100, cols=5)
        wks.update('A1', 'Activity')
        wks.update('B1', 'Done')
    
    # get all activities
    activities = wks.col_values(1)[1:]
    bot.reply_to(message, "Delete which activity?", reply_markup = reply_keyboard(activities))

# get all activites list
@bot.message_handler(commands=['list'])
def list_activity(message):
    # get username
    username = str(message.from_user.username)

    # check if the sheet is available for user
    try:
        wks = sheet.worksheet(username)
    except:
        wks = sheet.add_worksheet(username, rows=100, cols=5)
        wks.update('A1', 'Activity')
        wks.update('B1', 'Done')
    
    # get all activities
    activities = wks.get_all_values()
    if len(activities) < 2:
        bot.reply_to(message, "You have no activity added")
    else:
        response = construct_table(activities[1:])
        bot.reply_to(message, response, parse_mode='MarkdownV2')

# update
@bot.message_handler(commands=['update'])
def list_activity(message):
    # get argument
    args = message.text.split()[1:]
    activity = " ".join(args).lower()

    # get username
    username = str(message.from_user.username)

    # check if the sheet is available for user
    try:
        wks = sheet.worksheet(username)
    except:
        wks = sheet.add_worksheet(username, rows=100, cols=5)
        wks.update('A1', 'Activity')
        wks.update('B1', 'Done')

    # get all activities
    activities = wks.col_values(1)[1:]
    bot.reply_to(message, "Choose an activity", reply_markup = inline_keyboard(activities))

# delete function
@bot.callback_query_handler(func=lambda message: message.data.startswith('delete_'))
def delete_activity(callback_query):
    # get the task name from the callback query
    task = callback_query.data.split("_")[1]

    # delete activity
    wks = sheet.worksheet(str(callback_query.from_user.username))
    cell = wks.find(task)

    # The activity is not found
    if cell is None:
        bot.send_message(callback_query.message.chat.id, "The activity is not found")
        return
    
    wks.delete_rows(cell.row)

    # update the list
    activities = wks.col_values(1)[1:]
    bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=f"Delete which activity?", reply_markup=reply_keyboard(activities))
    bot.send_message(callback_query.message.chat.id, task + " has been deleted")

# yes no
@bot.callback_query_handler(func=lambda message: message.data.startswith('update_'))
def yesno_query(message):
    if message.message.chat.id != message.from_user.id:
        return

    # get the activity name from the callback query
    activity = message.data.split("_")[1]
    wks = sheet.worksheet(str(message.from_user.username))
    cell = wks.find(activity.lower())

    if cell is None:
        return

    status = message.data.split("_")[2]
    if status == 'yes':
        wks.update_cell(cell.row, 2, str(True))
    elif status == 'no':
        wks.update_cell(cell.row, 2, str(False))

    bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id, text=f"{activity} has been updated")

# cancel operation
@bot.callback_query_handler(func=lambda message: message.data.startswith('CANCEL'))
def cancel_query(callback_query):
    if callback_query.message.chat.id != callback_query.from_user.id:
        return
    bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

# update callback
@bot.callback_query_handler(func=lambda message: message.data.startswith('status_'))
def callback_query(activity):
    if activity.message.chat.id != activity.from_user.id:
        return

    # get the activity name from the callback query
    task = activity.data.split("_")[1]

    markup = InlineKeyboardMarkup(row_width=2)
    yes = InlineKeyboardButton('Yes', callback_data=f'update_{task}_yes')
    no = InlineKeyboardButton('No', callback_data=f'update_{task}_no')
    markup.add(yes, no)

    bot.send_message(activity.message.chat.id, text=f"{task} completed?", reply_markup=markup)

if __name__ == "__main__":
    with lock:
        try:
            bot.infinity_polling()
        except ConnectionResetError:
            pass        

