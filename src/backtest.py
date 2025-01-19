from DataHandler import HistoricDataHandler, LiveDataHandler
from Portfolio import Portfolio
from Risk import SimpleRiskHandler
from Broker import SimulateExecutionHandler
import strategies
from Metrics.metrics import Metrics

import pandas as pd
import numpy as np

import logging
import time

from tqdm import tqdm
from itertools import product, repeat
import multiprocessing as mp

import helper as h

import settings


class Backtester:
    def __init__(self):

        # Initialize modules
        if settings.MODE == "backtest":
            # change since this only works in jupyter notebook
            # self.dh = data_handler
            self.dh = HistoricDataHandler()
        #         else:  # settings.MODE == "paper" or settings.MODE == "live"
        #             self.dh = LiveDataHandler()

        self.portfolio = Portfolio(self.dh)
        self.broker = SimulateExecutionHandler(dh=self.dh, portfolio=self.portfolio)
        self.rh = SimpleRiskHandler(self.dh, self.portfolio, self.broker)

        self.portfolio.broker = self.broker

        # Load strategy module from string
        self.strategy = (
            getattr(strategies, settings.STRATEGY)()
            if settings.PARAMETERS is None
            else getattr(strategies, settings.STRATEGY)(**settings.PARAMETERS)
        )
        self.strategy.initialize(dh=self.dh, rh=self.rh)

    def run(self):
        try:
            for events in self.dh:
                for event in events:
                    if event.symbols:
                        if event.type_ == "BAR":
                            self.portfolio.update_value(event.symbols)
                            self.broker.check_orders(event)
                self.strategy.on_data(events)
                self.dh.sleep()
        except KeyboardInterrupt:
            print(pd.DataFrame(self.portfolio.holdings))
            self.dh.except_KI()

    @classmethod
    def reinitialize(cls):
        return cls(None)

    def optimize(self, metric, constraint, **kwargs):
        parameters = tuple(
            product(
                *(
                    # Flatten parameters
                    parameter
                    for parameter_bunch in (
                        (list(zip(repeat(pk), repeat(k), v)) for k, v in pv.items())
                        for pk, pv in kwargs.items()
                    )
                    for parameter in parameter_bunch
                )
            )
        )

        returns = np.zeros(len(parameters))
        # TODO: Multiprocessing
        # try:
        #     pool = mp.Pool(mp.cpu_count())
        map(self.opt, tqdm(range(len(parameters)), desc="Bunches"))
        # except:
        #     pass

        max_val = np.argmax(returns)
        bt = self.reinitialize()
        for parameter in parameters[max_val]:
            setattr(*(getattr(bt, parameter[0]), parameter[1], parameter[2]))
        bt.run()
        m = Metrics(portfolio=bt.portfolio, dh=bt.dh)
        print(m)

    def opt(self, idx):
        bt = self.reinitialize()
        for parameter in parameters[idx]:
            # print(idx, parameter)
            setattr(*(getattr(bt, parameter[0]), parameter[1], parameter[2]))
        bt.run()
        m = Metrics(portfolio=bt.portfolio, dh=bt.dh)
        returns[idx] = m.total_ret

    def metrics(self):
        # m = Metrics(portfolio=self.portfolio, dh=self.dh)
        # x = pd.DataFrame(self.portfolio.holdings)
        # print(x.iloc[30:40])
        print(Metrics(self.portfolio, self.dh))


# engine = Backtester()
# engine.run()
# # # print(engine.portfolio.holdings)
# engine.metrics()
# # engine.optimize(strategy={"window": range(10, 60)}, metric="returns", constraint=None)
