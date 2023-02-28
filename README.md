# telegram-bot-todolist
Telegram bot for doing to do list that you can share with friends. Integrate with Google Sheets API for database

# environment variables
`BOT_TOKEN` - telegram bot token get from botfather </br>
`SHEET` - google sheet name </br>
`GOOGLE_SHEET_CREDENTIALS` - google sheet credentials get from google cloud console

# commands

## add activity
`/add <activities>` - add new activities separated by commas ',' into the database 

## update activity
`/update` - update the activity status 

## list activities
`/list` - get all the list of activities and their status

## delete activity
`/delete` - delete an activity

## reset activities
`/reset` - reset all the activities status

### scheduler (SOON)
run overall summary activities for yesterday, reset back the database
