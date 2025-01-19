import numpy as np

from strategies import Strategy


class PredictiveStrategy(Strategy):
    def __init__(self, period=9):

        self.period = period

    def on_bar(self):
        data = self.dh.get_latest_data(self.symbol, columns="Close", N=self.period)

        price = data[-1]

        returns = np.diff(data) / data[:-1]

        up = returns[returns > 0]
        no_up = len(up)
        p_up = (no_up / len(returns)) * 100

        down = returns[returns < 0]
        no_down = len(down)
        p_down = (no_down / len(returns)) * 100

        if p_up > 70:
            return "LONG"

        if p_down < 30:
            return "SHORT"
