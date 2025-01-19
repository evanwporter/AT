from scipy import stats
import numpy as np

from strategies import Strategy


class LinearRegression(Strategy):
    def __init__(self, period=30, up_slope=1, down_slope=-1):

        self.period = period

        self.up_slope = up_slope
        self.down_slope = down_slope

    def on_bar(self):

        data = self.dh.get_latest_data(self.symbol, "Close", self.period)

        if len(data) >= self.period:
            slope = stats.linregress(np.arange(len(data)), data)[0]

            if slope > self.up_slope:
                return "LONG"

            # if slope < self.down_slope:
            #     return "SHORT"
