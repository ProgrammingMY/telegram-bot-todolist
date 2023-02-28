# telegram-bot-todolist
Telegram bot for doing to do list that you can share with friends. Integrate with Google Sheets API for database

# environment variables
BOT_TOKEN - telegram bot token get from botfather
SHEET - google sheet name
GOOGLE_SHEET_CREDENTIALS - google sheet credentials get from google cloud console

# commands

## add activity
/add activity - add new activity into the database 

## done activity
/done activity - update the activity status 

## list activities
/list - get all the list of activities and their status

## delete activity
/delete - delete an activity from username

## reset activities
/reset - reset all the activities from username

### scheduler (SOON)
run overall summary activities for yesterday, reset back the database
