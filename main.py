import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from IBClient import IBClient
from pprint import pprint
from typing import Dict
from typing import List

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(category=InsecureRequestWarning)


class Contract:
    def __init__(self, conid, ticker, expiry, put_or_call, strike, multiplier=100, currency="USD", und_conid=None):
        self.conid = conid
        self.ticker = ticker
        self.expiry = expiry
        self.put_or_call = put_or_call
        self.strike = strike
        self.multiplier = multiplier
        self.currency = currency
        self.und_conid = und_conid
        self.market_price = None
        self.und_price = None
        self.last_update = None

    def set_mkt_price(self, mkt_price):
        self.last_update = get_date_and_time()
        self.market_price = mkt_price

    def set_und_price(self, und_price):
        self.last_update = get_date_and_time()
        self.und_price = und_price


class Position:
    def __init__(self, contract, size, avg_price):
        self.contract = contract
        self.size = size
        self.avg_price = avg_price

    @staticmethod
    def parse_json_dict(json_dict: Dict):
        # todo add check if field is there
        # todo check it's option or stock
        conid = json_dict["conid"]
        ticker = json_dict["ticker"]
        expiry = json_dict["expiry"]
        put_or_call = json_dict['putOrCall']
        strike = json_dict["strike"]
        multiplier = json_dict["multiplier"]
        currency = json_dict["currency"]
        und_conid = json_dict["undConid"]
        contract = Contract(conid=conid,
                            ticker=ticker,
                            expiry=expiry,
                            put_or_call=put_or_call,
                            strike=strike,
                            multiplier=multiplier,
                            currency=currency,
                            und_conid=und_conid)

        mkt_price = json_dict["mktPrice"]
        contract.set_mkt_price(mkt_price)

        size = json_dict["position"]
        avg_price = json_dict["avgPrice"]
        position = Position(contract=contract, size=size, avg_price=avg_price)

        return position

    def to_json_dict(self, header : List[str]):
        json_dict = {}
        for field in header:
            if field == "lastUpdate":
                json_dict[field] = self.contract.last_update
            elif field == "conid":
                json_dict[field] = self.contract.conid
            elif field == "ticker":
                json_dict[field] = self.contract.ticker
            elif field == "undConid":
                json_dict[field] = self.contract.und_conid
            elif field == "expiry":
                json_dict[field] = self.contract.expiry
            elif field == "putOrCall":
                json_dict[field] = self.contract.put_or_call
            elif field == "strike":
                json_dict[field] = self.contract.strike
            elif field == "multiplier":
                json_dict[field] = self.contract.multiplier
            elif field == "mktPrice":
                json_dict[field] = self.contract.market_price
            elif field == "undPrice":
                json_dict[field] = self.contract.und_price
            elif field == "size":
                json_dict[field] = self.size
            elif field == "avgPrice":
                json_dict[field] = self.avg_price

        return json_dict


class Order:
    def __init__(self, contract, size, price, side, tif="DAY"):
        self.contract = contract
        self.size = size
        self.price = price
        self.side = side
        self.tif = tif


def update_positions_mkt_price(client, positions: List[Position]):
    und_conids = [pos.contract.und_conid for pos in positions]
    conids = [pos.contract.conid for pos in positions]
    prices = client.market_data(und_conids+conids)
    for pos in positions:
        contract = pos.contract
        contract.set_mkt_price(prices[contract.conid])
        contract.set_und_price(prices[contract.und_conid])


def get_account_id(client:IBClient):
    response = client.portfolio_accounts()
    account_id = response[0]["accountId"]
    return account_id


def get_positions(client:IBClient, account_id):
    page_id = 0
    positions = []
    while True:
        response = client.portfolio_account_positions(account_id=account_id, page_id=page_id)
        for pos_json in response:
            positions.append(Position.parse_json_dict(pos_json))
        if len(response) == 30:
            page_id += 1
        else:
            break

    return positions


def get_date_and_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


def write_google_sheet(positions: List[Position]):
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
        pos_json_dict = Position.to_json_dict(pos, headers)
        row = []
        for h in headers:
            value = str(pos_json_dict[h]) if h in pos_json_dict.keys() else ""
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
    Position.parse_json_dict(positions[0])
    #pprint(positions)

    #write_google_sheet()Sheet(positions)
    #conids = ["265598","37018770", "4762", "2586156"]
    #r = client.market_data(conids)
    #pprint(r)


if __name__ == '__main__':
    main()
