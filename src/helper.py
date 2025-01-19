import uuid
import enums
import arrow
import os
import settings as settings
import datetime as dt
import pandas as pd
import numpy as np
import exceptions


def interval_to_ms(interval: str):
    """Convert an interval string to milliseconds
    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {"m": 60, "h": 60 * 60, "d": 24 * 60 * 60, "w": 7 * 24 * 60 * 60}

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms


def generate_unique_id():
    return str(uuid.uuid4())


def find_id(l, id_):
    ret = list(filter(lambda x: x.id_ == id_, l))
    if len(ret) == 1:
        return ret[0]
    elif ret:
        return ret
    else:
        raise ValueError("Could not find {id} in {l}".format(id=id_, l=l))


def reverse_side(direction):
    if direction == enums.trade_type.LONG:
        return enums.side.SELL
    elif direction == enums.trade_type.SHORT:
        return enums.side.BUY
    else:
        raise ValueError(
            "Direction ({direction}) must be `LONG` or `SHORT`".format(
                direction=direction
            )
        )


def verify_routes(routes):
    for route in routes:
        # TODO: Check if strategy exists
        timeframe = route[2]
        if timeframe not in [
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "3h",
            "4h",
            "6h",
            "8h",
            "1D",
        ]:
            raise exceptions.InvalidRoute(
                'Timeframe "{}" is invalid. Supported timeframes are 1m, 3m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 6h, 8h, 1D'.format(
                    timeframe
                )
            )


def now():
    return arrow.utcnow().timestamp  # * 1000


def expand_timeframe(timeframe: str):
    timeframes = {"m": "minute", "h": "hour"}
    return timeframes[timeframe]


def strip_interval(interval):
    return int(interval[:-1]), interval[-1]


def csv_dir(symbol):
    return os.path.join(settings.DATA_DIRECTORY, "%s.csv" % symbol)


def check_datetime_like(datetime):
    if (
        (datetime is type(arrow.arrow))
        or (datetime is type(dt.datetime))
        or (datetime is type(pd.Timestamp))
        or (datetime is type(np.datetime64))
    ):
        return True
    else:
        return False


def check_timedelta_like(timedelta):
    if (
        (timedelta is type(dt.timedelta))
        or (timedelta is type(pd.Timedelta))
        or (timedelta is type(np.timedelta64))
    ):
        return True
    else:
        return False


def key(*args, **kwargs):
    if len(args) == 3:
        return "{}-{}{}".format(args[0], args[1], args[2])
    elif len(args) == 2:
        return "{}{}".format(args[0], args[1])
    elif "source" in kwargs:
        if "symbol" in kwargs:
            return "{}-{}".format(kwargs["source"], kwargs["symbol"])
        return "{}-{}{}".format(kwargs["source"], kwargs["base"], kwargs["quote"])
    return "{}{}".format(kwargs["base"], kwargs["quote"])


def split_symbol(symbol):
    return symbol.split("-")


def is_cash_like(symbol: str) -> bool:
    symbols = [
        "USDT",
        "USD",
        "USDC",
        "TUSD",
        "DAI",
    ]
    if symbol in symbols:
        return True
    return False
