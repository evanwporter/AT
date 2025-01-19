"""
DISCLAIMER: This entire folder is forked from `https://github.com/jesse-ai/jesse`
"""

import arrow
from tqdm import tqdm

import pandas as pd
import numpy as np

from datetime import datetime, timedelta, timezone
import time

from math import ceil

from .Drivers import Binance


def run(symbol, exchange, start_time, data=None):
    candles_ = []
    driver = Binance()
    start_date = arrow.get(start_time)
    until_date = arrow.utcnow().floor("day")
    days_count = (until_date - start_date).days
    candles_count = days_count * 1440  # Minutes in a day
    iterations = ceil(candles_count / 1000) + 1
    if data is None:
        data = pd.read_csv(
            r"C:\Users\evanh\Projects\AT\Data\%s.csv" % symbol, index_col=0, parse_dates=True
        )

    for _ in tqdm(range(iterations)):
        temp_start_timestamp = start_date.timestamp * 1000
        temp_end_timestamp = temp_start_timestamp + (driver.count - 1) * 60_000

        # to make sure it won't try to import candles from the future! LOL
        if temp_start_timestamp > (arrow.utcnow().timestamp * 1000):
            break

        # it's today's candles if temp_end_timestamp < now
        if temp_end_timestamp > (arrow.utcnow().timestamp * 1000):
            temp_end_timestamp = (
                arrow.utcnow().floor("minute").timestamp * 1000
            ) - 60_000

        # fetch from market
        candles = driver.fetch(symbol=symbol, start_timestamp=temp_start_timestamp)
        data_count = len(
            data.loc[(data.index > arrow.get(temp_start_timestamp).datetime) & (data.index <= arrow.get(temp_end_timestamp).datetime)]
        )
        exists = candles_count == data_count
        if not exists:
            if not len(candles):
                first_existing_timestamp = driver.get_starting_time(symbol)

                # if driver can't provide accurate get_starting_time()
                if first_existing_timestamp is None:
                    raise ValueError

                # handle when there's missing candles during the period
                if temp_start_timestamp > first_existing_timestamp:
                    # see if there are candles for the same date for the backup exchange,
                    # if so, get those, if not, download from that exchange.
                    driver.init_backup_exchange()
                    if driver.backup_exchange is not None:
                        candles = _get_candles_from_backup_exchange(
                            exchange,
                            driver.backup_exchange,
                            symbol,
                            temp_start_timestamp,
                            temp_end_timestamp,
                        )

        start_date = start_date.shift(minutes=driver.count)
        candles_ += candles
        time.sleep(driver.sleep_time)
    candles_ = pd.DataFrame(candles_)
    if not candles_.empty:
        cleaned_data = clean_data(candles_)
    else:
        cleaned_data = candles_
    return pd.concat((data, cleaned_data))


def clean_data(df):
   
    data = df.copy()
    
    start = data.Timestamp.iloc[0]
    end = data.Timestamp.iloc[-1]
    
    # Get rid of duplicates as they mess up the reindexing
    data = data.drop_duplicates("Timestamp").set_index("Timestamp")
    date_range = np.arange(start, end, step=60_000, dtype=np.float64)

    OHLC = data[['Open', 'High', 'Low', 'Close']].reindex(date_range, method='ffill')
    VOLUME = data[['Volume', 'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume',]].reindex(date_range, fill_value=0.0)
    reindexed_data = OHLC.join(VOLUME, how='outer')
    
    if len(reindexed_data) >= len(data):
        print("%d candles filled" % (len(reindexed_data) - len(df)))
    else:
        print("%d candles removed" % (len(df) - len(reindexed_data)))
        
    # Convert ms to datetime object i.e. make it readable
    times = (datetime.fromtimestamp(time/1000, timezone.utc) for time in data.index)
    data.index = times
    
    return data#.set_index("Timestamp")
