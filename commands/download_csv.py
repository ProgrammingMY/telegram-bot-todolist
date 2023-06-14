import boto3
import io
import pandas as pd

def converted_type(item):
    converted_item = {}
    for key, value in item.items():
        if 'S' in value:
            converted_item[key] = value['S']
        elif 'N' in value:
            converted_item[key] = value['N']
        elif 'B' in value:
            converted_item[key] = value['B']
        else:
            converted_item[key] = ''
    return converted_item

def download(bot, message):
    table_name = 'rsvp-loqmanxmira'
    dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1')

    try:
        # Get all items from the DynamoDB table
        response = dynamodb.scan(TableName=table_name)
        items = response['Items']

        # Convert DynamoDB types to Python types
        converted_items = [converted_type(item) for item in items]

        results = pd.DataFrame.from_dict(converted_items)
        
        # Create a CSV file in memory
        csv_file = io.StringIO()

        # Write the data to the CSV file
        results.to_csv(csv_file, index=False)

        csv_file.seek(0)
        csv_file.name = f'results.csv'
        
        # Send the CSV file to the user
        bot.send_document(chat_id=message.chat.id, document=csv_file)
    except Exception as e:
        bot.reply_to(message, 'An error occurred while downloading the CSV file.')
        print(e)
