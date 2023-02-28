from get_google_service import get_google_service

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

# get all activities and the status
def display_activities(bot, message):
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
    else:
        response = construct_table(activities[1:])
        bot.reply_to(message, response, parse_mode='MarkdownV2')