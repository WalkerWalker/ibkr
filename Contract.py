from datetime import datetime


class Contract:
    def __init__(self, conid, asset_class, contract_desc, currency, mkt_price):
        self.conid = conid
        self.asset_class = asset_class
        self.contract_desc = contract_desc
        self.currency = currency
        self.mkt_price = mkt_price
        self.last_update = self._date_and_time()
        self.und_conid = conid  # und means underlying, default for STK

        # for option contract
        self.ticker = None
        self.expiry = None
        self.strike = None
        self.put_or_call = None
        self.multiplier = None
        self.und_price = None  # und means underlying

    @staticmethod
    def _date_and_time():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def set_mkt_price(self, mkt_price):
        self.last_update = self._date_and_time()
        self.mkt_price = mkt_price

    def set_und_price(self, und_price):
        self.last_update = self._date_and_time()
        self.und_price = und_price

    def set_detail(self, detail):
        self.ticker = detail['ticker']

        if self.asset_class == "OPT":
            self.expiry = detail['expiry']
            self.strike = detail['strike']
            self.put_or_call = detail['putOrCall']
            self.multiplier = detail['multiplier']
            self.und_conid = detail['undConid']  # und means underlying