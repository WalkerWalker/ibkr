class Campaign:
    def __init__(self, und_conid, ticker, currency):
        self.und_conid = und_conid
        self.ticker = ticker
        self.currency = currency
        self.positions = []

        #attributes
        self.type = None # stock, short_put, short_call, short_put&short_call, poor_man_covered_call, pmcc&short_put
        self.margin = None
        self.implied_capital = None

    def add_position(self, position):
        # TODO: for the existing conid, adjust the size.
        self.positions.append(position)
        self._update_attributes()

    def _update_attributes(self):
        self._update_type()
        self._update_implied_capital()
        self._update_margin()

    def _update_type(self):
        pass

    def _update_margin(self):
        pass

    def _update_implied_capital(self):
        pass
