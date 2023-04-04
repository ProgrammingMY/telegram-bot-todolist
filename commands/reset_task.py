from get_google_service import get_google_service

# reset all activities to false
def reset_activities(bot, collection, message):
    # get id
    id = message.from_user.id

    # query all items and update it to false
    query = {"user": id}
    update = {"$set": {"done": False}}
    result = collection.update_many(query, update)

    # if no activity is found
    if result.modified_count == 0:
        bot.reply_to(message, "You have no activity added")
        return
    else:
        bot.reply_to(message, "All activities status have been reset")