import os
import json 
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account


def sheets_client():
    service_account_key = os.getenv('GOOGLE_SHEETS_KEY')
    if service_account_key:
        key = json.loads(service_account_key)
        credentials = service_account.Credentials.from_service_account_info(
            key)
        service = build('sheets', 'v4', credentials=credentials)
    else:
        # We're expecting the service account to be available in GCF
        service = build('sheets', 'v4', cache_discovery=False)
    return service.spreadsheets()

# Get a Google Sheets client
sheets = sheets_client()

def get_header_row(sheet_id, worksheet_name):

    cell_range = f"{worksheet_name}!1:1"
    cells = get_cells(sheet_id, cell_range)
    if len(cells)>0:
        return cells[0]
    else:
        return []

def get_row_data(sheet_id, worksheet_name, row_index):

    cell_range = f"{worksheet_name}!{row_index}:{row_index}"
    cells = get_cells(sheet_id, cell_range)
    if len(cells)>0:
        return cells[0]
    else:
        return []


def get_row_count(sheet_id, worksheet_name):
    
    # NB Ideally we'd only request A:A, but
    # If there are existing rows with a blank 
    # in the A column these will get overwritten.
    # We don't want that, so we request the 
    # whole sheet, just in case.
    # We're aiming for the timestamp to be in 
    # column A, but it could get moved so it's 
    # not guaranteed.
    cell_range = f"{worksheet_name}"
    return len(get_cells(sheet_id, cell_range))


def get_row(sheet_id, worksheet_name, column_index, row_value):
    
    columns = 'ABCDEFGHI'
    column=columns[column_index]
    cell_range = f"{worksheet_name}!{column}:{column}"
    print(f'Getting cells for range {cell_range}')
    values = get_cells(sheet_id, cell_range)
    print(f'Found {values}')
    row_values=[]
    # Unpack the [["row", "values"]] into a simple array
    for value in values:
        row_values.append(value[0])
    row_index = -1 if row_value not in row_values else row_values.index(row_value)
    print(f'row index {row_index}')
    return row_index + 1


def get_cells(sheet_id, cell_range):

    # Get the requested data
    result = sheets.values().get(spreadsheetId=sheet_id,
                                 range=cell_range).execute()
    return result.get('values', [])


def update_header_row(spreadsheet_row, sheet_id, worksheet_name):
    cell_range = f"{worksheet_name}!1:1"
    update_sheet([spreadsheet_row], sheet_id, cell_range)


def update_row(row, row_index, sheet_id, worksheet_name):
    cell_range = f"{worksheet_name}!{row_index}:{row_index}"
    print(f"Updating row {cell_range}")
    update_sheet([row], sheet_id, cell_range)


def update_sheet(data_table, sheet_id, cell_range):

    # Write the updated table to the spreadsheet
    sheets.values().update(spreadsheetId=sheet_id,
                           range=cell_range,
                           valueInputOption='USER_ENTERED',
                           body={
                               'values': data_table,
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
