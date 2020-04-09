import requests
import json
import os
import time
import base64
import threading
from flask import jsonify
from sheets import sheets_client, update_sheet, get_header_row, get_row_count, get_row, update_header_row, update_row, get_row_data


# Sheets config
sheet_id = os.getenv("SHEET_ID")
worksheet_name = os.getenv("WORKSHEET_NAME") or "Sheet1"


def sheets(event, context):
    """
    Update the output spreadsheet
    """

    #print(f"event: {event}")
    #print(f"context: {context}")

    # Process message data
    if 'data' in event:
        json_string = base64.b64decode(event['data']).decode('utf-8')
        message = json.loads(json_string)

        # Get a Google Sheets client
        client = sheets_client()

        # Update Status header row if needed
        status_header = get_header_row(sheet_id, worksheet_name, client)
        update = False
        if not 'last_update' in status_header:
            status_header.append('last_update')
            update = True
        if not 'code' in status_header:
            status_header.append('code')
            update = True
        for key in message:
            if not key in status_header:
                status_header.append(key)
                update = True
        if update:
            print("New columns found. Updating status_header row: {status_header}")
            update_header_row(status_header, sheet_id, worksheet_name, client)

        # Update History header row if needed
        history_header = get_header_row(sheet_id, "History", client)
        update = False
        if not 'last_update' in history_header:
            history_header.append('last_update')
            update = True
        if not 'code' in history_header:
            history_header.append('code')
            update = True
        for key in message:
            if not key in history_header:
                history_header.append(key)
                update = True
        if update:
            print("New columns found. Updating History history_header row: {history_header}")
            update_header_row(history_header, sheet_id, "History", client)

        # Find the row index on the status sheet
        site = message.get('site')
        print(f"Attempting to update row for site {site}")
        row_index = 0
        if 'site' in status_header:
            print('site column found in headers')
            column = status_header.index("site")
            print(f"Column index for 'site' is: {column}")
            row_index = get_row(sheet_id, worksheet_name, column, site, client)
            print(f'Got row index {row_index} for site {site}')
        if row_index < 1:
            print('no row index found')
            row_index = get_row_count(sheet_id, worksheet_name, client) + 1
            print(f"New row index is: {row_index}")
        
        
        # Build Status row values
        row_data = get_row_data(sheet_id, worksheet_name, row_index, client)
        row_update = []
        for i, key in enumerate(status_header):
            default = "" if i >= len(row_data) else row_data[i]
            row_update.append(str(message.get(key) or default))
        print(f'Status data is {row_update}')
        update_row(row_update, row_index, sheet_id, worksheet_name, client)
        
        
        # Add a row to the history of updates
        history_index = get_row_count(sheet_id, "History", client) + 1

        # Build History row values
        row_update = []
        for i, key in enumerate(history_header):
            default = "" if i >= len(row_data) else row_data[i]
            row_update.append(str(message.get(key) or ""))
        print(f'History data is {row_update}')
        update_row(row_update, history_index, sheet_id, "History", client)

        print("Sheet update sent.")




# def inventory(request):
#     """
#     Read a hospital inventory from spreadsheet
#     """

#     hospital = "Barts"
#     if 'hospital' in request.args:
#         hospital = request.args.get('hospital')
#     print(f"Getting data for {hospital}")
    
#     header = get_header_row(sheet_id, worksheet_name)
#     column_index = header.index("hospital")
#     row_index = get_row(sheet_id, worksheet_name, column_index, hospital)

#     row = []
#     if row_index > 0:
#         hospital_data = get_row_data(sheet_id, worksheet_name, row_index)
#         print(f"{row_index}: {hospital_data}")

#         if row_index > 1:
#             row = get_row_data(sheet_id, worksheet_name, row_index)

#     result = {}
#     if len(row) > 0:
#         for i in range(len(row)):
#             if i < len(header) and i < len(row):
#                 result[header[i]] = row[i]

#     print(f"Got row: {result}")
#     return jsonify(result)
