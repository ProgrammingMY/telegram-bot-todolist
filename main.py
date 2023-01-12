import os
import gspread
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
import telebot

acc = gspread.service_account()
sheet = acc.open(os.getenv('SHEET'))

commands = ['hi', 'hello', 'assalamualaikum', 'good']

bot = telebot.TeleBot(TOKEN, parse_mode=None)
print("Bot is online....")

status_map = {
    "true": "🟢",
    "false": "🔴"
}

def construct_table(data, spacing=30):
    spaces = " "
    #response = '\n'.join([''.join(['{:16}'.format(x) for x in r]) for r in data])
    response = "\n"
    for item in data:
        repeats = spacing - len(item[0])
        response += f"{item[0] : <{repeats}}{status_map[str(item[1]).lower()]}\n"

    return response

def get_message(message):
    message = message.text.split()
    if (message[0].lower() in commands):
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

# add a activity
@bot.message_handler(commands=['add'])
def add_activity(message):
    # get argument
    activity = message.text.split()[1].lower()

    # get username
    username = str(message.chat.username)

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
    # get argument
    activity = message.text.split()[1].lower()

    # get username
    username = str(message.chat.username)

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
        bot.reply_to(message, "No activity found")
    else:
        wks.delete_rows(cell.row)
        bot.reply_to(message, "Deleted")

# get all activites list
@bot.message_handler(commands=['list'])
def list_activity(message):
    # get username
    username = str(message.chat.username)

    # check if the sheet is available for user
    try:
        wks = sheet.worksheet(username)
    except:
        wks = sheet.add_worksheet(username, rows=100, cols=5)
        wks.update('A1', 'Activity')
        wks.update('B1', 'Done')
    
    # get all activities
    activities = wks.get_all_values()
    response = username + "'s activities\n"
    response += construct_table(activities[1:])

    bot.reply_to(message, response)

# update
@bot.message_handler(commands=['done'])
def list_activity(message):
    # get argument
    activity = message.text.split()[1].lower()

    # get username
    username = str(message.chat.username)

    # check if the sheet is available for user
    try:
        wks = sheet.worksheet(username)
    except:
        wks = sheet.add_worksheet(username, rows=100, cols=5)
        wks.update('A1', 'Activity')
        wks.update('B1', 'Done')

    # find row with the activity
    cell = wks.find(activity)
    
    # update status
    if cell is None:
        bot.reply_to(message, "No activity found")
    else:
        status = (wks.cell(cell.row, 2).value == 'TRUE')
        wks.update_cell(cell.row, 2, not status)
        bot.reply_to(message, "Update activity to " + str(not status))

@bot.message_handler(func=get_message)
def echo_all(message):
    bot.reply_to(message, "Howdy, how are you doing?")

bot.infinity_polling()