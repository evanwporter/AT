import settings

from strategies import Strategy


class BuyAndHold(Strategy):
    def __init__(self):
        self.name = "Buy and Hold"

        self.bought = {symbol: False for symbol in settings.SYMBOLS}

    def on_bar(self):

        if not self.bought[self.symbol]:
            self.bought[self.symbol] = True
            return "LONG"


class SellAndHold(Strategy):
    def __init__(self):
        self.name = "Sell and Hold"

        self.sold = {symbol: False for symbol in settings.SYMBOLS}

        def on_bar(self):

            if not self.sold[self.symbol]:
                self.sold[self.symbol] = True
                return "SHORT"
