import gspread
from oauth2client.service_account import ServiceAccountCredentials
from IBClient import IBClient
from Position import Position
from Campaign import Campaign

from pprint import pprint
from typing import List

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(category=InsecureRequestWarning)


def set_positions_detail(client, positions: List[Position]):
    conids = [pos.contract.conid for pos in positions]
    detail_list = client.contracts_definitions(conids)
    detail_dict = {}
    for detail in detail_list:
        detail_dict[detail['conid']] = detail
    for pos in positions:
        contract = pos.contract
        contract.set_detail(detail_dict[contract.conid])


def update_positions_mkt_price(client, positions: List[Position]):
    und_conids = [pos.contract.und_conid for pos in positions]
    conids = [pos.contract.conid for pos in positions]
    all_conids = und_conids + conids
    prices_list = client.market_data(all_conids)
    prices_dict = {}
    for json in prices_list:
        price = float(json['31'].strip("C")) # 31 is the last price in ib api
        prices_dict[json["conid"]] = price
    for pos in positions:
        contract = pos.contract
        contract.set_mkt_price(prices_dict[contract.conid])
        contract.set_und_price(prices_dict[contract.und_conid])


def get_campaigns(positions: List[Position]):
    campaigns = {}
    for pos in positions:
        und_conid = pos.contract.und_conid
        if und_conid not in campaigns.keys():
            ticker = pos.contract.ticker
            currency = pos.contract.currency
            campaign = Campaign(und_conid=und_conid, ticker=ticker, currency=currency)
            campaigns[und_conid] = campaign

        campaigns[und_conid].add_position(pos)
    return campaigns


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
            pos = Position.parse_json_dict(pos_json)
            if pos is not None:
                positions.append(pos)
        if len(response) == 30:
            page_id += 1
        else:
            break

    return positions


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

    account_id = get_account_id(client)
    positions = get_positions(client, account_id)

    set_positions_detail(client, positions)
    update_positions_mkt_price(client, positions)
    campaigns = get_campaigns(positions)

    for und_conid in campaigns.keys():
        print(und_conid, len(campaigns[und_conid].positions))
    #write_google_sheet(positions)


if __name__ == '__main__':
    main()
