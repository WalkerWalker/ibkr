from typing import Dict
from typing import List

class Campaign:
    def __init__(self, und_conid, ticker, currency):
        self.und_conid = und_conid
        self.ticker = ticker
        self.currency = currency
        self.positions = {}

        #attributes
        self.type = None # stock, short_put, short_call, short_put&short_call, poor_man_covered_call, pmcc&short_put
        self.margin = None
        self.implied_capital = None

    def add_position(self, position):
        # TODO: for the existing conid, adjust the size.
        self.positions[position.contract.conid] = position
        self._update_attributes()

    def _update_attributes(self):
        self.type = self._get_type()
        self._update_implied_capital()
        self._update_margin()

    def _get_type(self):
        type_set = set()
        for conid in self.positions.keys():
            pos = self.positions[conid]
            type_set.add(pos.type)
        if len(type_set) == 1:
            return type_set.pop()
        elif len(type_set) == 2:
            if type_set == {"SHORT PUT", "SHORT CALL"}:
                return "SHORT PUT&CALL" # TODO: distinguish straddle, swamp, strangle by strike price of call and put
            elif type_set == {"LONG CALL", "SHORT CALL"}:
                return "PMCC"
            elif type_set == {"LONG STK", "SHORT CALL"}:
                return "CC"
        elif len(type_set) ==3:
            if type_set == {"SHORT PUT", "SHORT CALL", "LONG CALL"}:
                return "PMCC & SHORT PUT"

        return "others"

    def _update_margin(self):
        pass

    def _update_implied_capital(self):
        pass

    def get_target_orders(self) -> List[Dict]:
        orders = []
        if self.type in {"SHORT PUT", "SHORT CALL"}:
            for conid in self.positions.keys():
                pos = self.positions[conid]
                orders.append(pos.get_close_order_json())

        return orders
