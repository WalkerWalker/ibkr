class Order:
    def __init__(self, contract, size, price, side, tif="DAY"):
        self.contract = contract
        self.size = size
        self.price = price
        self.side = side
        self.tif = tif
