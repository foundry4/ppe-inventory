import requests
import json
import os
import time
import base64
import threading
from operator import itemgetter
from sheets import update_sheet, get_header_row, get_row_count, get_row, update_header_row, update_row


# Sheets config
sheet_id = os.getenv("SHEET_ID")
worksheet_name = os.getenv("WORKSHEET_NAME") or "Sheet1"


def sheets(event, context):
    """
    Update the output spreadsheet
    """

    #print(f"event: {event}")
    #print(f"context: {context}")

    # Process attributes
    print(f"Attributes: {event.get('attributes')}")
    if 'attributes' in event:
        attributes = event['attributes']
        if 'timestamp' in attributes:
            timestamp = attributes['timestamp']
        else:
            print("Generating timestamp")
            timestamp = str(round(time.time()))
        if 'id' in attributes:
            id = attributes['id']
        else:
            print("Generating id")
            id = timestamp
    print(f"Timestamp: {timestamp}")
    print(f"ID: {id}")

    # Process message data
    if 'data' in event:
        json_string = base64.b64decode(event['data']).decode('utf-8')
        message = json.loads(json_string)
        message["timestamp"] = timestamp
        message["id"] = id

        # Update header row if needed
        header = get_header_row(sheet_id, worksheet_name)
        update = False
        if not 'timestamp' in header:
            header.append('timestamp')
            update = True
        if not 'id' in header:
            header.append('id')
            update = True
        for key in message:
            if not key in header:
                header.append(key)
                update = True
        if update:
            print("New columns found. Updating header row: {header}")
            update_header_row(header, sheet_id, worksheet_name)
        
        # Build row values
        row_data = []
        for key in header:
            row_data.append(str(message.get(key) or ""))

        # Add the row to the sheet
        row_index = 0
        if 'hospital' in header:
            print('hospital found in headers')
            column = header.index("hospital")
            print(f"Column index for {row_data[column]} is: {column}")
            row_index = get_row(sheet_id, worksheet_name, column, row_data[column])
            print(f'Got row index {row_index}')
        if row_index < 1:
            print('no row index found')
            row_index = get_row_count(sheet_id, worksheet_name) + 1
            print(f"New row index is: {row_index}")
        update_row(row_data, row_index, sheet_id, worksheet_name)

        print("Sheet update sent.")

