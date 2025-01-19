import pandas as pd
import numpy as np

from strategies import Strategy

# import talib

import datetime as dt


class BollingerBands(Strategy):
    type_ = "BAR"

    def __init__(self, method="TREND", window=dt.timedelta(days=24)):
        """Basic Bollinger Bands strategy

        Parameters
        ----------
        method : str, optional
            TREND or MR (for MEAN REVERSION), by default "TREND"
        window : int, optional
            window in which to calculate the bollinger bands, by default 24
        """
        self.name = "Bollinger Bands"
        self.method = method
        self.window = window

    def on_bar(self):

        data = self.dh.get_latest_data(self.symbol, N=self.window)

        self.price = data[-1]

        upperband, middleband, lowerband = talib.BBANDS(data, timeperiod=len(data))
        self.upper_band = upperband[-1]
        self.lower_band = lowerband[-1]

        if self.method == "MR":
            if self.lower_band > self.price:
                return "LONG"
            # elif self.upper_band < self.price:
            #     return "SHORT"
        else:
            if self.upper_band < self.price:
                return "LONG"
            # if self.lower_band > self.price:
            #     return "SHORT"

    # def plot(self):
    #     for symbol in self.symbols:
    #         data = self.data.get_latest_data(symbol, N=-1)
    #         df = pd.DataFrame(
    #             data, columns=['Symbol', 'Close Time', 'Close Price'])
    #         df = df.drop(['Symbol'], axis=1)
    #         df.set_index('Close Time', inplace=True)

    #         BollingerBands(df, window=20, config='UULL').plot()
