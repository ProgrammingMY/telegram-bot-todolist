from get_google_service import get_google_service

status_map = {
    "true": "🟢",
    "false": "🔴"
}

def construct_table(data, spacing=15):
    spaces = " "
    table = "```\n"
    for row in data:
        repeats = spacing - len(row['activity'])
        table += row['activity'] + (spaces*repeats) + status_map[str(row['done']).lower()] + "\n"

    table += " ```"
    return table

# get all activities and the status
def display_activities(bot, collection, message):
    # get id
    id = message.from_user.id
    
    # get all activities
    activities = collection.find({"user": id})
    response = construct_table(activities)
    if response == "```\n ```":
        bot.reply_to(message, "You have no activity added")
    else:
        bot.reply_to(message, response, parse_mode='MarkdownV2')