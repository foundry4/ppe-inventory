import requests
import json
import os
import time
import base64
from operator import itemgetter
from sheets import update_sheet, get_header_row, get_row_count, update_header_row, update_row


# Sheets config
sheet_id = os.getenv("SHEET_ID")
worksheet_name = os.getenv("WORKSHEET_NAME")


def sheets(event, context):
    """
    Update the output spreadsheet
    """

    #print(f"event: {event}")
    #print(f"context: {context}")

    # Process attributes
    print(f"Attributes: {event.get('attributes')}")
    if 'attributes' in event and 'timestamp' in event['attributes']:
        timestamp = event['attributes']['timestamp']
    else:
        print("Generating timestamp")
        timestamp = str(round(time.time()))
    print(f"Timestamp: {timestamp}")

    # Process message data
    if 'data' in event:
        json_string = base64.b64decode(event['data']).decode('utf-8')
        message = json.loads(json_string)

        # Update header row if needed
        header = get_header_row(sheet_id, worksheet_name)
        update = False
        if not 'timestamp' in header:
            header.append('timestamp')
        for key in message:
            if not key in header:
                header.append(key)
                update = True
        if update:
            print("New columns found. Updating header row: {header}")
            update_header_row(header, sheet_id, worksheet_name)
        
        # Build row values
        row = []
        for key in header:
            if key=='timestamp':
                row.append(timestamp)
            else:
                row.append(message.get(key) or "")
        row_index = get_row_count(sheet_id, worksheet_name) + 1
        print(f"New row index is: {row_index}")
        update_row(row, row_index, sheet_id, worksheet_name)
        print("Sheet update sent.")

