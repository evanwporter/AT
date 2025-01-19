from .exchange import CandleExchange

import requests


class Binance(CandleExchange):
    """
    """
    def __init__(self):
        super().__init__('Binance', 1000, 0.5)
        self.endpoint = 'https://www.binance.com/api/v1/klines'

    def get_starting_time(self, symbol):
        """
        :param symbol:
        :return:
        """
        payload = {
            'interval': '1d',
            'symbol': symbol,
            'limit': 1500,
        }

        response = requests.get(self.endpoint, params=payload)

        # Exchange In Maintenance
        if response.status_code == 502:
            raise ValueError('ERROR: 502 Bad Gateway. Please try again later')

        # unsupported symbol
        if response.status_code == 400:
            raise ValueError(response.json()['msg'])

        if response.status_code != 200:
            raise Exception(response.content)

        data = response.json()
        first_timestamp = int(data[0][0])
        # 60,000 ms in a minute
        # 1400 minutes in a day
        second_timestamp = first_timestamp + 60_000 * 1440

        return second_timestamp

    def fetch(self, symbol, start_timestamp):
        """
        note1: unlike Bitfinex, Binance does NOT skip candles with volume=0.
        note2: like Bitfinex, start_time includes the candle and so does the end_time.
        """
        end_timestamp = start_timestamp + (self.count - 1) * 60_000

        payload = {
            'interval': '1m',
            'symbol': symbol,
            'startTime': start_timestamp,
            'endTime': end_timestamp,
            'limit': self.count,
        }

        response = requests.get(self.endpoint, params=payload)

        data = response.json()

        # Exchange In Maintenance
        if response.status_code == 502:
            raise ValueError('ERROR: 502 Bad Gateway. Please try again later')

        # unsupported symbol
        if response.status_code == 400:
            raise ValueError(response.json()['msg'])

        candles = []

        for d in data:
            candles.append({
                'Timestamp': int(d[0]),
                'Open': float(d[1]),
                'High': float(d[2]),
                'Low': float(d[3]),
                'Close': float(d[4]),
                'Volume': float(d[5]),
                "Quote Asset Volume": float(d[7]),
                "Number of Trades": int(d[8]),
                "Taker Buy Base Asset Volume": float(d[9]),
                "Taker Buy Quote Asset Volume": float(d[10])
            })

        return candles