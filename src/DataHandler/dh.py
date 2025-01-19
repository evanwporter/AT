from abc import ABC, abstractmethod

import numpy as np

import settings

import datetime as dt

import sys

import logging

from DataHandler.symbol import Symbol


class DataHandler(ABC):
    def __init__(self):
        self.symbols = settings.SYMBOLS

    def get_latest_data(self, symbol: Symbol, columns="Close", N=-1, dtype=None):

        if not isinstance(symbol, Symbol):
            raise TypeError("%s must be type Symbol" % symbol)

        data_interval = self.symbols[symbol]["Timeframe"]["Data Interval"]

        if type(N) is dt.timedelta:
            if N < data_interval:
                N = data_interval
                logging.warning("Increasing N to one bar of data")
            else:
                N = N // data_interval

        if type(columns) != list and type(columns) != str:
            raise TypeError(
                "get_latest_data parameter 'columns' must be of type list or str"
            )

        data = self.latest_symbol_data[symbol][-N:]  # , dtype=object)

        if type(columns) == str:
            data = data[columns]  # self.symbols[symbol]["Columns"][columns]]
            if N == -1:
                data = data[0]

        else:
            if dtype is not None:
                return [
                    data[:, self.symbols[symbol]["Columns"][columns]].astype(dtype)
                    for column in columns
                ]
            else:
                return [
                    data[:, self.symbols[symbol]["Columns"][columns]]
                    for column in columns
                ]

        if dtype is not None:
            return data.astype(dtype)
        else:
            return data

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError("Should implement `iter`.")

    def sleep(self):
        pass

    @property
    def date(self):
        return self.dates[self.size - 1]

    def except_KI(self):
        sys.exit(0)
