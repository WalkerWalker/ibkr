import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

baseUrl = "https://localhost:5000/v1/portal"

def getAccountId():
    url = baseUrl + "/portfolio/accounts"
    content = requests.get(url, verify=False)
    id = content.json()[0]["accountId"]
    return id

def getPositions(accountId):
    pageId = 0
    positions = []

    while True:
        url = baseUrl + "/portfolio/" + accountId + "/positions/" + str(pageId)
        content = requests.get(url, verify=False)
        for pos in content.json():
            positions.append(pos)
        if len(content.json()) == 30:
            pageId += 1
        else:
            break

    return positions

def getDateAndTime():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def writeGoogleSheet(positions):
    spreadSheetName = "Options Tracker"
    sheetName = "Positions"
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    credential = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(credential)
    spreadsheet = client.open(spreadSheetName)
    sheet = spreadsheet.worksheet(sheetName)
    headers = sheet.row_values(1)
    sheet.clear()
    sheet.append_row(headers)
    rows = []
    for pos in positions:
        row = [getDateAndTime()]
        for h in headers[1:]:
            value = str(pos[h]) if h in pos.keys() else ""
            row.append(value)
        rows.append(row)
    spreadsheet.values_append(sheetName, {'valueInputOption': 'USER_ENTERED'}, {'values': rows})


accountId = getAccountId()
positions = getPositions(accountId)
writeGoogleSheet(positions)
