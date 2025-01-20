# Historic Data Handler
import os
import pandas as pd
import numpy as np
import logging
import json

from decimal import Decimal as D

from collections import OrderedDict

from DataHandler.event import *
from DataHandler.dh import DataHandler
from .symbol import Symbol

import helper as h

import exceptions as exceptions
import settings as settings

from datetime import timedelta


# TODO: Add support for slicing data
class HistoricDataHandler(DataHandler):
    def __init__(self):

        # store = pystore.store(settings.DATA_DIRECTORY)

        # -----------
        # | Private |
        # -----------
        self.symbol_data = {}
        self.trade_data = {}

        # ----------
        # | Public |
        # ----------
        # Creates a guide for each symbol data
        # The guide tells you in which row to find Open, Close, High, Low, ect.
        # Also it has information on the intervals
        # This information is pulled from the symbols file in the main package.
        self.symbols = settings.SYMBOLS

        logging.info("Trading %s." % self.symbols)

        # # Unique values
        # # ie: (USDT, BTC, XRP) if trading with BTCUSDT & XRPUSDT
        # self.split_symbols = set(
        #     # TODO: Create a subclass of the symbol class for this
        #     s
        #     for symbol in self.symbols
        #     for s in symbol
        # )

        # This is the "known data"
        self.latest_symbol_data = {symbol: None for symbol in self.symbols.keys()}

        # Warmup period is how many the starting point for the data. Everything in the
        # warmup period can be used as data right from the start.
        self.warmup_period: int = settings.DATA_WARMUP_PERIOD

        self._parse_df()

    def _parse_df(self):

        # self.dates is the master the compilation of all of the trades intervals.
        self.dates = np.array([], dtype="datetime64[ns]")

        trading_data: dict[Symbol, pd.DataFrame] = {}

        for symbol in self.symbols.keys():

            file_path = f"{settings.DATA_DIRECTORY}/{symbol}.csv"

            if not os.path.exists(file_path):
                logging.warning(
                    f"Data file for symbol '{symbol}' not found: {file_path}"
                )
                continue

            # Two different intervals of interest
            # Each asset has both of these intervals
            # Trade Interval: how often the bot should trade
            # Data Interval: how much of the pricing database should be revealed to the strategy class

            # DataFrame
            # Sets the index column to 0 (dates)
            # Converts the index to pandas datetime
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            except Exception as e:
                logging.error(f"Failed to load data for symbol '{symbol}': {e}")
                continue

            if data.empty:
                logging.warning(
                    f"Data file for symbol '{symbol}' is empty: {file_path}"
                )
                continue

            parameters = self.symbols[symbol]

            # Convert evertthing to np.timedelta64
            data_interval = parameters["Data Interval"]
            trading_interval = parameters["Trading Interval"]
            if type(data_interval) is str:
                data_interval = np.timedelta64(
                    data_interval[:-1], data_interval[-1]
                ).astype(timedelta)
                parameters["Data Interval"] = data_interval
            if type(trading_interval) is str:
                trading_interval = np.timedelta64(
                    trading_interval[:-1], trading_interval[-1]
                ).astype(timedelta)
                parameters["Trading Interval"] = trading_interval

            # Ensure necessary columns exist
            required_columns = {"Open", "High", "Low", "Close", "Volume"}
            if not required_columns.issubset(data.columns):
                logging.error(
                    f"Missing required columns in data for symbol '{symbol}': {file_path}"
                )
                continue

            # Convert to decimal for extra precision
            data[["Open", "High", "Low", "Close"]] = (
                data[["Open", "High", "Low", "Close"]].astype(str).map(D)  # type: ignore
            )

            # Resampling is very important since it makes sure that the
            # program only reveals the data we want it to reveal
            OHLC = (
                data.resample(rule=data_interval)  # type: ignore
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
                data.drop(columns=["Open", "High", "Low", "Close"]).resample(  # type: ignore
                    rule=data_interval  # type: ignore
                )
                # This sums up the volume for the entire data_interval
                .sum()
            )

            OHLCV = pd.concat((OHLC, V), axis=1)

            # Market data tbat will be accessed by other parts of the program
            self.symbol_data[symbol] = OHLCV

            trading_data[symbol] = OHLCV.asfreq(trading_interval)

            # Creates an index of all the trading intervals
            self.dates = np.sort(
                np.unique(
                    np.concatenate([self.dates, trading_data[symbol].index.to_numpy()])
                )
            )

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
            bar = BarEvent(pd.Timestamp(self.date))
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
