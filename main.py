import gspread
from oauth2client.service_account import ServiceAccountCredentials
from IBClient import IBClient
from Position import Position
from Campaign import Campaign

from pprint import pprint
from typing import Dict

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(category=InsecureRequestWarning)


def set_positions_detail(client, positions: Dict[int, Position]):
    conids = positions.keys()
    detail_list = client.contracts_definitions(list(conids))
    detail_dict = {}
    for detail in detail_list:
        detail_dict[detail['conid']] = detail
    for conid in positions.keys():
        pos = positions[conid]
        contract = pos.contract
        contract.set_detail(detail_dict[conid])
        pos.set_type()


def update_positions_mkt_price(client, positions: Dict[int, Position]):
    conids = positions.keys()
    und_conids = [positions[conid].contract.und_conid for conid in conids]
    all_conids = und_conids + list(conids)
    prices_list = client.market_data(all_conids)
    prices_dict = {}
    for json in prices_list:
        price = float(json['31'].strip("C")) # 31 is the last price in ib api
        prices_dict[json["conid"]] = price
    for conid in positions.keys():
        contract = positions[conid].contract
        contract.set_mkt_price(prices_dict[contract.conid])
        contract.set_und_price(prices_dict[contract.und_conid])


def get_campaigns(positions: Dict[int, Position]) -> Dict[int, Campaign]:
    campaigns = {}
    for conid in positions.keys():
        pos = positions[conid]
        und_conid = pos.contract.und_conid
        if und_conid not in campaigns.keys():
            ticker = pos.contract.ticker
            currency = pos.contract.currency
            campaign = Campaign(und_conid=und_conid, ticker=ticker, currency=currency)
            campaigns[und_conid] = campaign

        campaigns[und_conid].add_position(pos)
    return campaigns


def get_account_id(client: IBClient) -> str:
    response = client.portfolio_accounts()
    account_id = response[0]["accountId"]
    return account_id


def get_positions(client: IBClient, account_id) -> Dict[int, Position]:
    page_id = 0
    positions = {}
    while True:
        response = client.portfolio_account_positions(account_id=account_id, page_id=page_id)
        for pos_json in response:
            pos = Position.parse_json_dict(pos_json)
            if pos is not None:
                positions[pos.contract.conid] = pos
        if len(response) == 30:
            page_id += 1
        else:
            break

    return positions


def write_google_sheet(positions: Dict[int, Position]):
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
    for conid in positions.keys():
        pos = positions[conid]
        pos_json_dict = pos.to_json_dict(headers)
        row = []
        for h in headers:
            value = str(pos_json_dict[h]) if h in pos_json_dict.keys() else ""
            row.append(value)
        rows.append(row)
    spreadsheet.values_append(sheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': rows})


def clear_orders(client, account_id: str):
    orders = client.get_live_orders()
    for order in orders["orders"]:
        if order["status"] not in {"Cancelled", "Inactive"}:
            order_id = order["orderId"]
            response = client.delete_order(account_id=account_id, order_id=order_id)


def place_order_with_confirm(client, account_id, order):
    # look if order_ref is occupied.
    # order_ref = order['cOID']
    # occupied = False
    # orders = client.get_live_orders()
    # for live_order in orders["orders"]:
    #     if live_order["order_ref"] == order_ref:
    #         occupied = True
    #         print(live_order)
    #         live_order_id = live_order['orderId']
    #         client.delete_order(account_id, live_order_id)
    #         break
    #
    # # if order_ref is occupied, use the order_id to modify order, otherwise place a new order
    # if occupied:
    #     content = client.modify_order(account_id=account_id, local_order_id=order_ref, order=order)
    # else:
    #     content = client.place_order(account_id=account_id, order=order)
    #
    # if content is None:
    #     print(occupied)

    content = client.place_order(account_id=account_id, order=order)
    while True:
        question = content[0]  # TODO: add check
        if 'id' in question:
            reply_id = question['id']
            content = client.place_order_reply(reply_id, True)
        else:
            break
    return content


def clear_and_place_target_orders(client, account_id: str, campaigns: Dict[int, Campaign]):
    clear_orders(client, account_id)
    target_orders = []
    for und_conid in campaigns.keys():
        camp = campaigns[und_conid]
        target_orders.extend(camp.get_target_orders())

    for order in target_orders:
        response = place_order_with_confirm(client, account_id, order)
        pprint(response)

    #orders = client.get_live_orders()
    #pprint(orders["orders"])


def main():
    client = IBClient()

    account_id = get_account_id(client)
    positions = get_positions(client, account_id)

    set_positions_detail(client, positions)
    update_positions_mkt_price(client, positions)
    campaigns = get_campaigns(positions)

    # clear_orders(client, account_id)
    # orders = client.get_live_orders()
    # for order in orders['orders']:
    #     if order['status'] not in {"Cancelled", "Inactive"}:
    #         pprint(order)
    #     else:
    #         pprint(order['order_ref'])
    clear_and_place_target_orders(client, account_id, campaigns)


    #write_google_sheet(positions)


if __name__ == '__main__':
    main()
