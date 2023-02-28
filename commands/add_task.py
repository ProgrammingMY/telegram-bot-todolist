# import get_google_service
from get_google_service import get_google_service

# add task function
def add_activity(bot, message):
    # get argument
    args = message.text.split()[1:]
    if args == []:
        return

    # get array of activities separated by comma
    # eliminate space in front and back of each activity
    activities = [activity.strip() for activity in " ".join(args).split(",")]

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

    # store all activities into sheet
    for activity in activities:
        wks.append_row([activity, str(False)], table_range="A1:B1")

    bot.reply_to(message, "Added activity(s) successfully")
