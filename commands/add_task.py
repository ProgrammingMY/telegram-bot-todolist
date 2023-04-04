# import get_google_service
from get_google_service import get_google_service

# add task function
def add_activity(bot, collection, message):
    # get argument
    args = message.text.split()[1:]
    if args == []:
        return

    # get array of activities separated by comma
    # eliminate space in front and back of each activity
    activities = [activity.strip() for activity in " ".join(args).split(",")]

    # get id from message
    id = message.from_user.id

    # create new activity
    new_activities = []
    for activity in activities:
        new_activity = {
            "user": id,
            "activity": activity,
            "done": False
        }
        new_activities.append(new_activity)

    # insert new activity into database
    try:
        collection.insert_many(new_activities)
        return bot.reply_to(message, "Added activity(s) successfully")
    except:
        return bot.reply_to(message, "Error: Cannot connect to database")
    
