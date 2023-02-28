from get_google_service import get_google_service

# reset all activities to false
def reset_activities(bot, message):
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
    activities = wks.get_all_values()
    if len(activities) < 2:
        bot.reply_to(message, "You have no activity added")
        return

    # reset all activities to false
    for i in range(2, len(activities)+1):
        wks.update(f'B{i}', 'False')

    bot.reply_to(message, "All activities status have been reset")