import requests
import json
import os
import time
import base64
from operator import itemgetter
from sheets import update_sheet


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
    attributes = event.get('attributes')
    if 'attibutes' in event and 'timestamp' in event['attributes']:
        timestamp = attributes.get('timestamp')
    else:
        print("Generating timestamp")
        timestamp = str(round(time.time()))
    print(f"Timestamp: {timestamp}")

    # Process message data
    if 'data' in event:
        message = base64.b64decode(event['data']).decode('utf-8')

    print(f"{timestamp}: {message}")

    table = []
    header = ["id", "message"]
    table.append(header)
    spreadsheet_row = [timestamp, message]
    table.append(spreadsheet_row)

    # Update the spreadsheet
    update_sheet(table, sheet_id, worksheet_name)

    print("Sheet update sent.")

