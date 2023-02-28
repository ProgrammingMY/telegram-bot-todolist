import gspread
import os
import json
from dotenv import load_dotenv

# get google sheet service
def get_google_service():
    # load environment variables
    load_dotenv()

    # get the credentials from the environment variable
    credentials = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS"))

    # get the service
    gc = gspread.service_account_from_dict(credentials)

    # open the sheet
    sh = gc.open(os.getenv("SHEET"))
    return sh