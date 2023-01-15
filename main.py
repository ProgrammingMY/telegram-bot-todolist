import os
import gspread
import threading
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

acc = gspread.service_account(filename="/etc/secrets/service_account.json")
sheet = acc.open(os.getenv('SHEET'))
lock = threading.Lock()

awaiting_response = False
data = {}

# contruct inline keyboard button
def markup_inline(activities):
    global data
    global awaiting_response
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for activity in activities:
        button = KeyboardButton(activity)
        keyboard.add(button)
    awaiting_response = True

    return keyboard

def inline_keyboard(items):
    markup = InlineKeyboardMarkup(row_width=1)
    for item in items:
        button = InlineKeyboardButton(item, callback_data=item)
        markup.add(button)

    return markup

bot = telebot.TeleBot(TOKEN, parse_mode=None)
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
    bot.reply_to(message, "Delete which activity?", reply_markup = markup_inline(activities))

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
@bot.message_handler(content_types=['text'])
def delete_activity(activity):
    global awaiting_response
    global data
    if awaiting_response:
        # delete activity
        wks = sheet.worksheet(str(activity.from_user.username))
        cell = wks.find(activity.text.lower())

        # The activity is not found
        if cell is None:
            bot.send_message(activity.chat.id, "The activity is not found", reply_markup=ReplyKeyboardRemove())
            return
        
        wks.delete_rows(cell.row)
        bot.send_message(activity.chat.id, activity.text + " has been deleted", reply_markup=ReplyKeyboardRemove())
        awaiting_response = False

# yes no
@bot.callback_query_handler(func=lambda message: message.data in ['yes', 'no'])
def yesno_query(message):
    global data
    # get the data from first callback (activity)
    activity = data[message.message.chat.id]

    wks = sheet.worksheet(str(message.from_user.username))
    cell = wks.find(activity.lower())

    if cell is None:
        data = {}
        return

    if message.data == 'yes':
        wks.update_cell(cell.row, 2, str(True))
        bot.send_message(message.message.chat.id, activity + " has been updated")
    elif message.data == 'no':
        wks.update_cell(cell.row, 2, str(False))
        bot.send_message(message.message.chat.id, activity + " has been updated")

    data = {}

# update callback
@bot.callback_query_handler(func=lambda message: True)
def callback_query(activity):
    # store the data from first callback
    data[activity.message.chat.id] = activity.data

    markup = InlineKeyboardMarkup(row_width=2)
    yes = InlineKeyboardButton('Done', callback_data='yes')
    no = InlineKeyboardButton('Not Done', callback_data='no')
    markup.add(yes, no)

    bot.send_message(activity.message.chat.id, "What is the status?", reply_markup=markup)

if __name__ == "__main__":
    with lock:
        try:
            bot.polling()
        except ConnectionResetError:
            pass

