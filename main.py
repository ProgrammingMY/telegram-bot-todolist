import os
from dotenv import load_dotenv
import telebot
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# commands all commands
from commands import add_task, delete_task, update_task, read_tasks, reset_task

# connect to bot
bot = telebot.TeleBot(TOKEN)
print("Bot is online....")

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
def add(message):
    add_task.add_activity(bot, message)

# reset all activities to false status
@bot.message_handler(commands=['reset'])
def reset_activity(message):
    reset_task.reset_activities(bot, message)

# get all activites list
@bot.message_handler(commands=['list'])
def list_activity(message):
    read_tasks.display_activities(bot, message)

#########delete activity#########
# delete an activity, display first
@bot.message_handler(commands=['delete'])
def delete_activity(message):
    delete_task.display_activity(bot, message)

# delete the selected activity
@bot.callback_query_handler(func=lambda message: message.data.startswith('delete_'))
def delete_activity(callback_query):
    delete_task.delete_activity(bot, callback_query)

#########update activity#########
# update an activity, display first
@bot.message_handler(commands=['update'])
def display_activity(message):
    update_task.display_activity(bot, message)

# selected an activity to update
@bot.callback_query_handler(func=lambda message: message.data.startswith('status_'))
def callback_query(activity):
    update_task.select_activity(bot, activity)

# update to true or false
@bot.callback_query_handler(func=lambda message: message.data.startswith('update_'))
def yesno_query(callback_query):
    update_task.update_activity(bot, callback_query)

# cancel operation
@bot.callback_query_handler(func=lambda message: message.data.startswith('CANCEL'))
def cancel_query(callback_query):
    # ensure the correct user that interact with the button
    if callback_query.message.reply_to_message.from_user.id != callback_query.from_user.id:
        return
    
    bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

if __name__ == "__main__":
    try:
        bot.infinity_polling()
    except ConnectionResetError:
        pass        