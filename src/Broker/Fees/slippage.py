import settings


class SlippageModel:
    def __init__(self, dh):
        self.dh = dh
        self.lag = int(settings.SLIPPAGE_LAG)

        if self.lag < 1:
            raise ValueError(
                "Slippage lag interval must be a whole number that is 1 or greater"
            )

    def __call__(self, symbol, price):
        return price
        # return price - self.dh.total_data[symbol]["Close"].iloc[self.dh.size + self.lag]
