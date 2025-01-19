from dataclasses import dataclass

class Symbol:
    # Using slots is faster
    # https://stackoverflow.com/questions/472000/usage-of-slots
    __slots__ = [
        "source",
        "_base",
        "_quote"
    ]
    def __init__(self, source, base, quote):
        self.source: str = source
        self._base: str = base
        self._quote: str = quote

    def __hash__(self):
        return hash(self.symbol)

    def __repr__(self):
        return self.symbol

    def __iter__(self):
        for s in (self.base, self.quote):
            yield s
    
    @property
    def symbol(self):
        return "{}-{}{}".format(self.source, self._base, self._quote)

    @property
    def base(self):
        return "{}-{}".format(self.source, self._base)

    @property
    def quote(self):
        return "{}-{}".format(self.source, self._quote)

    @property
    def symbol_no_source(self):
        return "{}{}".format(self._base, self._quote)

# print([s for s in Symbol("Binance", "BTC", "USDT")])