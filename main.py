import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

baseUrl = "https://localhost:5000/v1/portal"

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(category=InsecureRequestWarning)

class Contract:
    def __init__(self, conid, ticker, expire, callput, strike, multiplier=100, currency="USD"):
        self.conid = conid
        self.ticker = ticker
        self.expire = expire
        self.callput = callput
        self.strike = strike
        self.multiplier = multiplier
        self.currency = currency


class Position:
    def __init__(self, contract, size, opendate, premium, fee):
        self.contract = contract
        self.size = size
        self.opendate = opendate
        self.premium = premium
        self.fee = fee

    def updatePrice(self, stockPrice, optionPrice):
        #TODO
        pass

class Order:
    def __init__(self, contract, size, price, side, tif="DAY"):
        self.contract = contract
        self.size = size
        self.price = price
        self.side = side
        self.tif = tif

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

def getLastPrice(conids):
    #TODO do a better job at authentication
    url = baseUrl + "/iserver/reauthenticate"
    content = requests.post(url, verify=False)

    url = baseUrl + "/iserver/accounts"
    content = requests.get(url, verify=False)

    url = baseUrl + "/iserver/marketdata/snapshot"
    delimiter = ','
    conids_list = delimiter.join(conids)
    params ={"conids": conids_list,
             "fields": "31"}
    content = requests.get(url, params, verify=False)
    content = requests.get(url, params, verify=False)  # run twice to get it right.
    price_values = []
    for item in content.json():
        price_values.append({item['conid']: item['31']})
    return price_values

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


#accountId = getAccountId()
#positions = getPositions(accountId)
#writeGoogleSheet(positions)
r = getLastPrice(["265598","37018770", "4762", "2586156"])
print(r)
