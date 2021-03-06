from typing import Dict
from typing import List
from Contract import Contract


class Position:
    def __init__(self, contract, size, avg_price):
        self.contract = contract
        self.size = size
        self.avg_price = avg_price
        self.type = None

    @staticmethod
    def parse_json_dict(json_dict: Dict):
        # todo add check if field is there
        # todo check it's option or stock
        size = json_dict["position"]
        if size == 0:
            return None

        conid = json_dict["conid"]
        asset_class = json_dict['assetClass']
        currency = json_dict["currency"]
        mkt_price = json_dict["mktPrice"]
        contract = Contract(conid=conid,
                            asset_class=asset_class,
                            currency=currency,
                            mkt_price=mkt_price)

        size = json_dict["position"]
        avg_price = json_dict["avgPrice"]
        position = Position(contract=contract, size=size, avg_price=avg_price)

        return position

    def to_json_dict(self, header=None):
        if header is None:
            header = ['conid', 'mktPrice', 'undPrice']
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
            elif field == 'currency':
                json_dict[field] = self.contract.currency
            elif field == "mktPrice":
                json_dict[field] = self.contract.mkt_price
            elif field == "undPrice":
                json_dict[field] = self.contract.und_price
            elif field == "size":
                json_dict[field] = self.size
            elif field == "avgPrice":
                json_dict[field] = self.avg_price
            elif field == "dte":
                json_dict[field] = self.contract.dte
            elif field == "extrinsic":
                json_dict[field] = self.contract.extrinsic
            elif field == "intrinsic":
                json_dict[field] = self.contract.intrinsic
            elif field == "ann_extrinsic":
                json_dict[field] = self.contract.ann_extrinsic
            elif field == "target":
                json_dict[field] = self.contract.target

        return json_dict

    def set_type(self):
        self.type = self._get_type()

    def _get_type(self) -> str:
        if self.contract.asset_class == "STK":
            if self.size > 0:
                return "LONG STK"
            elif self.size < 0:
                return "SHORT STK"
        elif self.contract.put_or_call == "P":
            if self.size > 0:
                return "LONG PUT"
            elif self.size < 0:
                return "SHORT PUT"
        elif self.contract.put_or_call == "C":
            if self.size > 0:
                return "LONG CALL"
            elif self.size < 0:
                return "SHORT CALL"

        return "NIL"

    def get_close_order_json(self) -> Dict:
        order = {}
        order["conid"] = self.contract.conid
        order["secType"] = str(self.contract.conid) + ":" + self.contract.asset_class
        # order["cOID"] = "CLOSE-" + str(self.contract.conid)
        order["orderType"] = "LMT"
        order["price"] = self.contract.target
        order["side"] = "BUY" if self.size < 0 else "SELL"
        order["quantity"] = abs(self.size)
        order["tif"] = "DAY"
        return order
