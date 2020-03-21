import os
import json 
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



def update_sheet(spreadsheet_table, sheet_id, cell_range):

    # Get a Google Sheets client
    sheets = sheets_client()

    # Get the current data
    print(f"spreadsheetId: {sheet_id}")
    print(f"range: {cell_range}")
    result = sheets.values().get(spreadsheetId=sheet_id,
                                 range=cell_range).execute()
    values = result.get('values', [])

    # Update the data table
    overwrite_data(values, spreadsheet_table)

    # Write the updated table to the spreadsheet
    sheets.values().update(spreadsheetId=sheet_id,
                           range=cell_range,
                           valueInputOption='USER_ENTERED',
                           body={
                               'values': values,
                               'majorDimension': 'ROWS'
                           }).execute()


def overwrite_data(old_table, new_table):

    # Clear the existing table so we're not left with cling-ons
    for row in old_table:
        for c in range(len(row)):
            row[c] = ""

    # Write in the new data, expanding as necessary
    for r in range(len(new_table)):
        new_row = new_table[r]

        if r >= len(old_table):
            # Append more rows
            old_table.append(new_row)
        else:
            old_row = old_table[r]
            for c in range(len(new_row)):
                if c < len(old_row):
                    # Update existing cells in the row
                    old_row[c] = new_row[c]
                else:
                    # Append more cells to the row
                    old_row.append(new_row[c])


def sheets_client():
    service_account_key = os.getenv('GOOGLE_SHEETS_KEY')
    if service_account_key:
        key = json.loads(service_account_key)
        credentials = service_account.Credentials.from_service_account_info(
            key)
        service = build('sheets', 'v4', credentials=credentials)
    else:
        # We're expecting the service account to be available in GCF
        service = build('sheets', 'v4')
    return service.spreadsheets()
