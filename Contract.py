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

        # moneyness
        self.dte = None
        self.intrinsic = None
        self.extrinsic = None
        self.ann_extrinsic = None
        self.target = None

    @staticmethod
    def _date_and_time():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def _get_ann_target(dte):
        # TODO: adjust ann_target by dte
        return 0.1

    def _set_moneyness(self):
        expiry = datetime.strptime(self.expiry, "%Y%m%d")
        self.dte = (expiry - datetime.now()).days
        if self.put_or_call == "P":
            self.intrinsic = max(0, -self.und_price+self.strike)
        else:
            self.intrinsic = max(0, self.und_price-self.strike)
        self.extrinsic  = self.mkt_price - self.intrinsic
        self.ann_extrinsic = self.extrinsic/self.strike * (365/self.dte)

        ann_target = self._get_ann_target(self.dte)
        self.target = ann_target * self.strike * self.dte/365
        self.target = round(self.target, 2)

    def set_mkt_price(self, mkt_price):
        self.last_update = self._date_and_time()
        self.mkt_price = mkt_price
        if self.asset_class == "OPT" and self.mkt_price is not None and self.und_price is not None:
            self._set_moneyness()

    def set_und_price(self, und_price):
        self.last_update = self._date_and_time()
        self.und_price = und_price
        if self.asset_class == "OPT" and self.mkt_price is not None and self.und_price is not None:
            self._set_moneyness()

    def set_detail(self, detail):
        self.ticker = detail['ticker']

        if self.asset_class == "OPT":
            self.expiry = detail['expiry']
            self.strike = detail['strike']
            self.put_or_call = detail['putOrCall']
            self.multiplier = detail['multiplier']
            self.und_conid = detail['undConid']  # und means underlying