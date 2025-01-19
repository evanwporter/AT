import numpy as np
cimport numpy as np
import pandas as pd

cimport cython

import matplotlib.pyplot as plt


cdef class Metrics:
    cdef:
        object holdings, returns # DataFrames
        object dh, portfolio

        public list closed_trades

        object trade_data

        # object portfolio
        
        public np.float64_t[:] eq_curve
        public np.float64_t max_dd, dd_duration, total_R
        object avg_hold_time

        int number_trades

    def __init__(self, portfolio, dh):        
        self.holdings = (
            pd.DataFrame(
                list(portfolio.holdings), 
                dtype=np.float64
            )
        )

        self.portfolio = portfolio
        # self.closed_trades = list(self.portfolio.closed_trades)
        self.dh = dh

        self.returns = self.holdings['Total Equity'].pct_change() #.diff().div(self.holdings['Total Equity'].shift(1))
        self.eq_curve = (1.0 + self.returns).cumprod().to_numpy()
            
    cdef np.float64_t max_leverage(self):
        return self.holdings['Leverage'].max()

    cdef np.float64_t total_return(self):
        return ((self.eq_curve[-1] - 1.0) * 100.0)
    
    @property
    def total_ret(self):
        return self.total_return()

    cdef np.float64_t pnl(self):
        return self.holdings["Total Equity"].iloc[-1] - self.holdings["Total Equity"].iloc[0]
        
    @cython.boundscheck(False)
    cdef void _calculate_drawdown(self):
        cdef np.ndarray[np.float64_t] high_water_mark = np.zeros(len(self.eq_curve), dtype=np.float64)
        cdef np.ndarray[np.float64_t] drawdown = np.zeros(len(self.eq_curve), dtype=np.float64)
        cdef np.ndarray[np.float64_t] drawdown_duration = np.zeros(len(self.eq_curve), dtype=np.float64)
       
        cdef int t
        for t in range(1, len(self.eq_curve)):
            high_water_mark[t] = max(high_water_mark[t-1], self.eq_curve[t])
            drawdown[t]= high_water_mark[t] - self.eq_curve[t]
            drawdown_duration[t]= 0 if drawdown[t] == 0 else drawdown_duration[t-1] + 1
        
        self.max_dd = drawdown.max()
        self.dd_duration = drawdown_duration.max()

    cdef np.float64_t sharpe_ratio(self, int periods=252):
        return (np.sqrt(periods) * np.mean(self.returns)) / np.std(self.returns)

    def __repr__(self):
        # self._trade_stats()
        self._calculate_drawdown()

        stats = {
            "Total Return": "%0.2f%%" % self.total_return(),
            "Sharpe Ratio": "%0.2f" % self.sharpe_ratio(),
            "Max Drawdown": "%0.2f%%" % (self.max_dd * 100.0),
            "Drawdown Duration": "%d" % self.dd_duration,
            "Maximum Leverage": "%0.2f" % self.max_leverage(),
            # "Number of Trades": "%d" % self.number_trades,
            # "Average Holding Time": str(self.avg_hold_time),
            # "Total R": "%0.2f" % self.total_R,
            # "Profit and Loss": "$%0.2f" % self.pnl(),
            # "System Quality Number": "%0.2f" % self.sqn()
        }
        return self._stats_to_table(stats)

    @staticmethod
    def _stats_to_table(stats):
        col_width_k = max([len(key) for key in stats])
        col_width_v = max([len(value) for value in stats.values()])
        
        top_row = "+" + "-" * (col_width_k + col_width_v + 6) + "+\n"
        title =  "| Metrics"
        title_row = title + " " * (col_width_k + col_width_v + 7 - len(title)) + "|\n"
        
        table_begin_end = "+%s--+%s---+\n" % ("-" * col_width_k, "-" * col_width_v)

        l = [
            "| "
            + "|".join(
                [
                    "{:{}} ".format(key, col_width_k),
                    " {:{}}  |\n".format(value, col_width_v),
                ]
            )
            for key, value in stats.items()
        ]

        return "{0}{1}{2}{3}{2}".format(top_row, title_row, table_begin_end, "".join(l))
    
    cdef np.float64_t sqn(self):
        """
        Van Tharp's System Quality Number
        Score: 1.6 - 1.9 Below average, but trade-able
        Score: 2.0 - 2.4 Average
        Score: 2.5 - 2.9 Good
        Score: 3.0 - 5.0 Excellent
        Score: 5.1 - 6.9 Superb
        Score: 7.0 - Keep this up, and you may have the Holy Grail.
        
        Scoring source: `https://www.quantshare.com/item-1541-system-quality-number-indicator`
        """
        return np.sqrt(self.number_trades) * self.trade_data["PnL"].mean() / (self.trade_data["PnL"].std() or np.nan)
    
    cdef void _trade_stats(self):
        cdef str symbol
        cdef object price
        cdef object date
        cdef object trade

        for symbol in self.dh.symbols:
            price = self.dh.get_latest_data(symbol, "Close")
            date = self.dh.date

            for trade in self.portfolio.trades[symbol]:
                trade.close_price = price
                trade.close_date = date
                self.closed_trades.append(trade)

        self.trade_data = pd.DataFrame([vars(trade) for trade in self.closed_trades])
        self.trade_data["PnL"] = self.trade_data.quantity * (self.trade_data.close_price - self.trade_data.open_price)
        self.trade_data["R"] = (self.trade_data.open_price - self.trade_data.stop_loss) / self.trade_data.PnL
        self.trade_data["Duration"] = self.trade_data.close_date - self.trade_data.open_date

        self.number_trades = len(self.trade_data)
        self.avg_hold_time = self.trade_data.Duration.mean()
        self.total_R = self.trade_data.R.sum()
        
    def plot_holdings(self):
        # print(self.holdings['Total Equity'])
        self.holdings.index = self.dh.dates
        self.holdings['Total Equity'].plot()
        plt.show()