import requests
import json
import os
import time
import base64
import threading
from flask import jsonify
from sheets import update_sheet, get_header_row, get_row_count, get_row, update_header_row, update_row, get_row_data


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

        # Update header row if needed
        header = get_header_row(sheet_id, worksheet_name)
        update = False
        if not 'last_update' in header:
            header.append('last_update')
            update = True
        if not 'code' in header:
            header.append('code')
            update = True
        for key in message:
            if not key in header:
                header.append(key)
                update = True
        if update:
            print("New columns found. Updating header row: {header}")
            update_header_row(header, sheet_id, worksheet_name)
            update_header_row(header, sheet_id, "History")

        # Add the row to the sheet
        site = message.get('site')
        row_index = 0
        if 'site' in header:
            print('site column found in headers')
            column = header.index("site")
            print(f"Column index for 'site' is: {column}")
            row_index = get_row(sheet_id, worksheet_name, column, site)
            print(f'Got row index {row_index} for site {site}')
        if row_index < 1:
            print('no row index found')
            row_index = get_row_count(sheet_id, worksheet_name) + 1
            print(f"New row index is: {row_index}")
        
        # For the history of updates
        history_index = get_row_count(sheet_id, "History") + 1
        
        
        # Build row values
        row_data = get_row_data(sheet_id, worksheet_name, row_index)
        row_update = []
        for i, key in enumerate(header):
            default = "" if i >= len(row_data) else row_data[i]
            row_update.append(str(message.get(key) or default))
        print(f'Row data is {row_update}')
        update_row(row_update, row_index, sheet_id, worksheet_name)
        update_row(row_update, history_index, sheet_id, "History")

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
