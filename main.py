import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from IBClient import IBClient
from pprint import pprint

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(category=InsecureRequestWarning)

from typing import Dict
from typing import List

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
    def __init__(self, contract, size, opendate, avgPrice):
        self.contract = contract
        self.size = size
        self.opendate = opendate
        self.avgPrice = avgPrice

    def update_price(self, stockPrice, optionPrice):
        #TODO
        pass

    @staticmethod
    def parse_json(json: Dict):
        #todo add check if field is there
        conid = json["conid"]
        pprint(json)

class Order:
    def __init__(self, contract, size, price, side, tif="DAY"):
        self.contract = contract
        self.size = size
        self.price = price
        self.side = side
        self.tif = tif


def get_account_id(client:IBClient):
    response = client.portfolio_accounts()
    account_id = response[0]["accountId"]
    return account_id


def get_positions(client:IBClient, account_id):
    page_id = 0
    positions = []
    while True:
        response = client.portfolio_account_positions(account_id=account_id, page_id=page_id)
        positions.extend(response)
        if len(response) == 30:
            page_id += 1
        else:
            break

    return positions


def get_date_and_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


def write_google_sheet(positions):
    spread_sheet_name = "Options Tracker"
    sheet_name = "Positions"
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    credential = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(credential)
    spreadsheet = client.open(spread_sheet_name)
    sheet = spreadsheet.worksheet(sheet_name)
    headers = sheet.row_values(1)
    sheet.clear()
    sheet.append_row(headers)
    rows = []
    for pos in positions:
        row = [get_date_and_time()]
        for h in headers[1:]:
            value = str(pos[h]) if h in pos.keys() else ""
            row.append(value)
        rows.append(row)
    spreadsheet.values_append(sheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': rows})


def main():
    client = IBClient()
    client.validate_SSO()
    client.reauthenticate()
    r = client.authentication_status()

    account_id = get_account_id(client)
    positions = get_positions(client, account_id)
    Position.parse_json(positions[0])
    #pprint(positions)

    #write_google_sheet()Sheet(positions)
    #conids = ["265598","37018770", "4762", "2586156"]
    #r = client.market_data(conids)
    #pprint(r)


if __name__ == '__main__':
    main()
