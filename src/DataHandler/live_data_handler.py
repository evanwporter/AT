from .dh import DataHandler
from .event import BarEvent
from .Data import Binance, run

import arrow
from datetime import datetime, timedelta
import time

import numpy as np
import pandas as pd

import settings as settings

import helper as h


class LiveDataHandler(DataHandler):
    def __init__(self):
        super().__init__()

        # self.exchange = Binance()
        # # self.data_interval = settings.DATA_INTERVAL
        # # self.data_delta = np.timedelta64(int(self.data_interval[:-1]), self.data_interval[-1]).astype(datetime)

        self.trading_interval = "1h"
        self.trading_delta = np.timedelta64(
            *h.strip_interval(self.trading_interval)
        ).astype(timedelta)

        # # Get all date up to start_time
        self.latest_symbol_data = {}
        self.time = arrow.utcnow().ceil("minutes")

        for symbol in self.symbols:
            start_date = pd.read_csv(
                h.csv_dir(symbol), parse_dates=True, index_col=0
            ).index[-1] + timedelta(minutes=1)
            self.latest_symbol_data[symbol] = run(symbol, "Binance", start_date)

        # Get all data

    def __iter__(self):
        while True:
            event = DataEvent(None)
            for symbol in self.symbols:
                data = run(
                    symbol, "Binance", self.time, data=self.latest_symbol_data[symbol]
                )
                self.dates = data.index
                self.latest_symbol_data[symbol] = data.to_numpy()
                event.symbols.append(symbol)
            self.size = len(data)
            yield event

            # Get Data

    def sleep(self):
        self.time += self.trading_delta

        now = arrow.utcnow()
        sleep_time = (self.time - now).total_seconds()

        if sleep_time < 0:
            raise ValueError("Sleep time (%d) is less than zero" % sleep_time)

        time.sleep(sleep_time)

    def except_KI(self):
        for symbol in self.symbols:
            df = pd.DataFrame(self.latest_symbol_data[symbol])
            df.index = self.dates
            df.columns = self.symbols[symbol]["Columns"]
            # df.to_csv(h.csv_dir(symbol) + "1")
        super().except_KI()
