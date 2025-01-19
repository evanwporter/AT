import pandas as pd
import numpy as np

from math import floor

import matplotlib.pyplot as plt
import seaborn as sns

import talib

from hrp import HierarchicalRiskParity


class RiskHandler:
    def __init__(
        self,
        events,
        dh,
        portfolio,
        # max_leverage=0,
        # weight_calculation_period=-1,
        # shorting=False,
    ):
        self.events = events

        self.dh = dh
        self.symbols = self.dh.symbols

        self.portfolio = portfolio
        self.holdings = self.portfolio.holdings
        self.positions = self.portfolio.positions

        # self.weight_calculation_period = (
        #     weight_calculation_period  # Everything by default
        # )
        
        # self.shorting = shorting

        # self.hrp = HierarchicalRiskParity(list(self.symbols))

        # self.shorts = {symbol: 1 for symbol in self.symbols}

        # self.idx = -1

        np.seterr(all='raise')

    def _optimal_weight(self, symbol, short_side, idx):
        """Using Hierarchical Risk Parity becuase it makes the most 
        sense to me. 
        
        It works like so: It divides the assets into groups based on
        correlation. Then, treating each of the groups as a single asset 
        it calculates the weights using an inverse volatility weighting 
        scheme. Which is basically a way to give less volatile assets more 
        weight in a portfolio and more volatile assets less weight.

        Parameters
        ----------
        symbol : str
            Asset symbol to find the optimal weight of.
        short_side : bool
            Tell the optimal weight calculator whether to 
            be on the short side for a particular symbol or not.

        Returns
        -------
        np.float64
            The optimal weight of the given symbol according to the 
            Hierarchical Risk Parity optimizer.
        """
        if short_side:
            self.shorts[symbol] = -1
        else:
            self.shorts[symbol] = 1

        prices = np.array(
            [
                np.array(
                    list(zip(*self.dh.latest_symbol_data[s]))[
                        self.dh.symbols[symbol]["Columns"]["Close"]
                    ]
                )
                for s in self.symbols
            ],
            dtype=np.float64,
        ).T
        prices = prices[~np.isnan(prices).any(axis=1)].T

        if idx != self.idx:
            self.idx = idx + 1
            return self.hrp.optimize(
                asset_prices=prices, side_weights=self.shorts.values()
            )[list(self.symbols).index(symbol)]
        else:
            return self.hrp.build_long_short_portfolio(
                self.hrp.weights, self.shorts.values()
            )[list(self.symbols).index(symbol)]

    def _calculate_weights(self, event, total_equity):
        symbol = event.symbol
        signal_type = event.signal_type

        if signal_type == "SHORT":
            short_side = True
        else:
            short_side = False

        optimal_size = (
            self._optimal_weight(symbol, short_side, event.index) * total_equity
        )
        current_size = self.positions[symbol].market_value

        if current_size == optimal_size:
            return 0
        elif signal_type == "LONG":
            if current_size < optimal_size:
                # Room to increase size
                q = self._bet_size(event, total_equity)
                return self._bet_size(event, total_equity)
            elif current_size > optimal_size:
                # Must decrease size to optimal_size
                return -self._bet_size(event, total_equity)
        elif signal_type == "SHORT":
            if current_size > optimal_size:
                # Room to decrease size
                return -self._bet_size(event, total_equity)
            elif current_size < optimal_size:
                # Must increase size to optimal_size
                return self._bet_size(event, total_equity)

    def _bet_size(self, event, total_eq, **kwargs):
        """[summary]

        Parameters
        ----------
        event : SignalEvent
            [description]
        total_eq : [type]
            [description]
        method : dict, optional
            Fixed Quantity: {"name": "fixed quantity", "quantity": 1}
            Fixed Percent of Cash: {"name": "fixed % $", "percent": .05}
            Kelly Criterion: {"name": "kelly", "period": 50}


        Returns
        -------
        float
            Quantity
        """

        symbol = event.symbol
        
        return .01

    def on_signal(self, event):
        
        total_eq = self.holdings[-1]["Total Equity"]

        quantity = self._bet_size(event, total_eq)

        if quantity != 0:

            if event.direction == "LONG":
                direction = 'BUY'
            else:
                direction = "SELL"

            self.events.append(
                OrderEvent(
                    date=event.date,
                    symbol=event.symbol,
                    price=event.price,
                    order_type="MARKET",
                    quantity=quantity,
                    direction=direction,
                )
            )
    
    def _stop_loss(self, event, quantity, period=100):
        data = [np.array(
            list(zip(*self.dh.get_latest_data(event.symbol, N=period)))[2:],
            dtype=np.float64,
        )[self.symbols[event.symbol]['Columns']['%s' % (column)]] for column in ['High', "Low", "Close"]]# + [period]
       
        volatility = (3 * talib.ATR(*data))[-1]
        price = event.price

        if event.signal_type == 'LONG':
            stop_loss = price - volatility
        else: # event.signal_type == 'SHORT'
            stop_loss = price + volatility
        
        self.events.append(
            OrderEvent(
                symbol=event.symbol,
                price=stop_loss,
                order_type="LIMIT",
                quantity=-quantity,
                direction="NA",
            )
        )
