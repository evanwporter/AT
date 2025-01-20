from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt
import pandas as pd

import settings as settings

import datetime as dt

import sys

import logging

from DataHandler.symbol import Symbol


class DataHandler(ABC):

    latest_symbol_data: dict[Symbol, pd.DataFrame | None]
    symbols: dict[Symbol, dict[str, str]]
    dates: npt.NDArray[np.datetime64]
    size: int
    trade_data: dict[Symbol, npt.NDArray[np.bool_]]
    symbol_data: dict[Symbol, pd.DataFrame]

    def __init__(self):
        self.symbols = settings.SYMBOLS

    def get_latest_data(
        self,
        symbol: Symbol,
        columns: str | list[str] = "Close",
        N: int = -1,
        dtype=None,
    ) -> (
        None
        | pd.Series
        | pd.DataFrame
        | np.ndarray
        | list[np.ndarray]
        | list[pd.Series]
        | int
    ):

        if not isinstance(symbol, Symbol):
            raise TypeError("%s must be type Symbol" % symbol)

        data_interval: str = self.symbols[symbol]["Data Interval"]

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

        latest_data = self.latest_symbol_data.get(symbol)
        if latest_data is None:
            logging.warning(f"No data available for symbol {symbol}")
            return None

        data = latest_data[-N:]

        if type(columns) == str:
            data = data[columns]  # self.symbols[symbol]["Columns"][columns]]
            if N == -1:
                data = data[0]

        else:
            if dtype is not None:
                return [data[:, column].astype(dtype) for column in columns]
            else:
                return [data[:, column] for column in columns]

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
    def date(self) -> np.datetime64:
        return self.dates[self.size - 1]

    def except_KI(self):
        sys.exit(0)
