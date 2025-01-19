# Historic Data Handler
import pandas as pd
import numpy as np

from decimal import Decimal as D

from collections import OrderedDict, defaultdict

import json

from DataHandler.event import *
from DataHandler.dh import DataHandler
from DataHandler.symbol import Symbol

import helper as h

import exceptions as exceptions
import settings as settings
from symbols import symbols as syms

from datetime import timedelta


# TODO: Add support for slicing data
class HistoricDataHandler(DataHandler):
    def __init__(self):

        # store = pystore.store(settings.DATA_DIRECTORY)

        with open(r".\AT\symbol_info.json") as info:
            self.symbol_info = json.load(info)

        # -----------
        # | Private |
        # -----------
        self.symbol_data = {}
        self.trade_data = {}
        self.total_data = {}

        # ----------
        # | Public |
        # ----------
        # Creates a guide for each symbol data
        # The guide tells you in which row to find Open, Close, High, Low, ect.
        # Also it has information on the intervals
        # This information is pulled from the symbols file in the main package.
        self.symbols = {
            Symbol(*self._split_symbol(symbol, source)): syms[source][symbol]
            for source, symbols in settings.SYMBOLS.items()
            for symbol in symbols
        }

        self.exchanges = set([symbol.source for symbol in self.symbols])

        # This will be changed in the future.
        if len(self.exchanges) > 1:
            raise ValueError(
                "To many exchanges. At the moment we can only trade on one exhange"
            )

        logging.info("Trading on %s." % self.exchanges)

        logging.info("Trading %s." % self.symbols.items())

        # Unique values
        # ie: (USDT, BTC, XRP) if trading with BTCUSDT & XRPUSDT
        self.split_symbols = set(
            # TODO: Create a subclass of the symbol class for this
            s
            for symbol in self.symbols
            for s in symbol
        )

        # This is the "known data"
        self.latest_symbol_data = {symbol: None for symbol in self.symbols}

        # Warmup period is how many the starting point for the data. Everything in the
        # warmup period can be used as data right from the start.
        self.warmup_period = settings.DATA_WARMUP_PERIOD

        self._parse_df()

    def _split_symbol(self, symbol, source=None):
        if source is None:
            source, symbol = h.split_symbol(symbol)

        base = self.symbol_info[symbol]["baseAsset"]
        quote = self.symbol_info[symbol]["quoteAsset"]

        return source, base, quote

    def _parse_df(self):

        # self.dates is the master the compilation of all of the trades intervals.
        self.dates = pd.Index([])

        trading_data = {}

        for symbol in self.symbols.keys():

            # Two different intervals of interest
            # Each asset has both of these intervals
            # Trade Interval: how often the bot should trade
            # Data Interval: how much of the pricing database should be revealed to the strategy class

            # DataFrame
            # Sets the index column to 0 (dates)
            # Converts the index to pandas datetime
            data = pd.read_csv(
                "%s\\%s.csv" % (settings.DATA_DIRECTORY, str(symbol)),
                index_col=0,
                parse_dates=True,
            )

            parameters = self.symbols[symbol]

            # Convert evertthing to np.timedelta64
            data_interval = parameters["Timeframe"]["Data Interval"]
            trading_interval = parameters["Timeframe"]["Trading Interval"]
            if type(data_interval) is str:
                data_interval = np.timedelta64(
                    data_interval[:-1], data_interval[-1]
                ).astype(timedelta)
                parameters["Timeframe"]["Data Interval"] = data_interval
            if type(trading_interval) is str:
                trading_interval = np.timedelta64(
                    trading_interval[:-1], trading_interval[-1]
                ).astype(timedelta)
                parameters["Timeframe"]["Trading Interval"] = trading_interval

            # Convert to decimal for extra precision
            data[["Open", "High", "Low", "Close"]] = (
                data[["Open", "High", "Low", "Close"]].astype(str).applymap(D)
            )

            # Resampling is very important since it makes sure that the
            # program only reveals the data we want it to reveal
            OHLC = (
                data.resample(rule=data_interval)
                # This converts it back to a dataframe
                # Each of the functions takes a particular price from the time period
                # ie: Open get the first price in the time period
                # ie: High takes the highest price
                .agg(
                    OrderedDict(
                        (
                            ("Open", "first"),
                            ("High", "max"),
                            ("Low", "min"),
                            ("Close", "last"),
                        )
                    )
                )
                # Fills in empty values with the previous value
                .ffill()
            )

            V = (
                data.drop(columns=["Open", "High", "Low", "Close"]).resample(
                    rule=data_interval
                )
                # This sums up the volume for the entire data_interval
                .sum()
            )

            OHLCV = pd.concat((OHLC, V), axis=1)

            # Market data tbat will be accessed by other parts of the program
            self.symbol_data[symbol] = OHLCV

            trading_data[symbol] = OHLCV.asfreq(trading_interval)

            # Creates an index of all the trading intervals
            self.dates = self.dates.union(trading_data[symbol].index)

        # Must be done after self.dates is full formed
        for symbol in self.symbols.keys():
            # Creating trading index that
            # tells how often to trade
            # and when to load the data from
            # a symbol
            self.trade_data[symbol] = (
                trading_data[symbol]
                # Expands the trading_data to encompass all of self.dates
                # Blanks are filled in with NaN
                .reindex(self.dates)
                # Marks False for cells with NaN
                .notnull()
                # Any rows with False, is marked as False
                # This converts it from a DataFrame to a Series
                .all(axis=1)
                # Now its just a 1d array
                .to_numpy(dtype=bool)
            )

        # -------------------------------------------------------------
        # Unimplemented Sentiment Stuff
        # for symbol, parameters in self.symbols.items():
        # if h.split_symbol(symbol)[0] == "Twitter":
        #     trading_interval = trading_interval
        #     data.date = pd.to_datetime(
        #         data.date, format="%Y-%m-%d %H:%M:%S+00:00", utc=True
        #     )
        #     data.set_index("date", inplace=True)
        #     self.symbol_data[symbol] = [
        #         df for date, df in data.resample(rule=trading_interval)
        #     ]
        #     self.market_data[symbol] = pd.DataFrame(
        #         {"date": date, "empty": np.nan if df.empty else 0}
        #         for date, df in data.resample(rule=trading_interval)
        #     ).set_index("date")
        # -------------------------------------------------------------

    def __iter__(self):

        for self.size in range(len(self.dates)):
            bar = BarEvent(self.date)
            #             sentiment = SentimentEvent(self.date)

            for symbol in self.symbols.keys():
                if self.trade_data[symbol][self.size]:

                    # -------------------------------------------------------------
                    # Unimplemented Sentiment Stuff
                    # if h.split_symbol(symbol)[0] == "Twitter":
                    #     self.latest_symbol_data[symbol] = self.symbol_data[symbol][
                    #         self.size
                    #     ]
                    #     sentiment.symbols[symbol] = self.sp.split_symbol(symbol, include_source=True)
                    # else:
                    # -------------------------------------------------------------

                    self.latest_symbol_data[symbol] = self.symbol_data[symbol][
                        : self.date
                    ]

                    #                     if self.latest_symbol_data[symbol] is None:
                    #                         self.latest_symbol_data[symbol] = next(self.symbol_data[symbol])
                    #                     else:
                    #                         # Get the latest bar and adds it to the table of bars.
                    #                         self.latest_symbol_data[symbol] = np.concatenate(
                    #                             (
                    #                                 self.latest_symbol_data[symbol],
                    #                                 next(self.symbol_data[symbol]),
                    #                             )
                    #                         )
                    bar.symbols.append(symbol)

            if self.size >= self.warmup_period:
                yield [bar]  # , sentiment]
