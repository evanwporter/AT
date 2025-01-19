import numpy as np
import pandas as pd

from loop import Backtester
from cMetric import cMetrics


class Optimize:
    
    def optimize_strategy_parameter(self, parameter):
        df = pd.DataFrame(columns=['Return'])
        for p in np.arange(7, 101):
            bt = Backtester('PredictiveStrategy')
            setattr(bt.strategy, parameter, p)
            bt.backtest()
            metrics = cMetrics(bt.portfolio)
            df.loc[p, 'Return'] = ((metrics.total_return - 1.0) * 100)
        # print(df.loc[df.Return == df.Return.max()])

    def create_benchmark_strategy(self):
        self.benchmark_strategy = Backtester("BuyAndHold")


optimal = Optimize()
print(optimal.optimize_strategy_parameter('period'))
