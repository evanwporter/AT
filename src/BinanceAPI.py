from urllib.parse import urlencode
import time
import hashlib
import requests
import hmac

class Binance:
    
    BASE_URL = "https://www.binance.com/api/v1"
    BASE_URL_V3 = "https://api.binance.us/api/v3"
    PUBLIC_URL = "https://www.binance.com/exchange/public/product"

    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret

    def ping(self):
        path = "%s/ping" % self.BASE_URL_V3
        return requests.get(path, timeout=30, verify=True).json()
    
    def get_history(self, symbol, limit=50):
        path = "%s/historicalTrades" % self.BASE_URL
        params = {"symbol": symbol, "limit": limit}
        return self._get_no_sign(path, params)
        
    def get_trades(self, market, limit=50):
        path = "%s/trades" % self.BASE_URL
        params = {"symbol": symbol, "limit": limit}
        return self._get_no_sign(path, params)
        
    def get_candles(self, symbol, interval, startTime, endTime):
        # [0]  Open time
        # [1]  Open
        # [2]  High
        # [3]  Low
        # [4]  Close
        # [5]  Volume
        # [6]  Close time
        # [7]  Quote asset volume
        # [8]  Number of trades
        # [9]  Taker buy base asset volume
        # [10] Taker buy quote asset volume
        # [11] Ignore.
        path = "%s/klines" % self.BASE_URL_V3
        params = {"symbol": market, "interval":interval, "startTime":startTime, "endTime":endTime}
        return self._get_no_sign(path, params)
        
    def get_ticker(self, market):
        path = "%s/ticker/24hr" % self.BASE_URL
        params = {"symbol": market}
        return self._get_no_sign(path, params)

    def get_order_book(self, symbol, limit=50):
        path = "%s/depth" % self.BASE_URL
        params = {"symbol": symbol, "limit": limit}
        return self._get_no_sign(path, params)

    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=30, verify=True).json()
    
    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def _get(self, path, params={}):
        params.update({"recvWindow": config.recv_window})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        return requests.get(url, headers=header, \
            timeout=30, verify=True).json()

    def _post(self, path, params={}):
        params.update({"recvWindow": config.recv_window})
        query = urlencode(self._sign(params))
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, data=query, \
            timeout=30, verify=True).json()

    def _order(self, market, quantity, side, rate=None):
        params = {}
         
        if rate is not None:
            params["type"] = "LIMIT"
            params["price"] = self._format(rate)
            params["timeInForce"] = "GTC"
        else:
            params["type"] = "MARKET"

        params["symbol"] = market
        params["side"] = side
        params["quantity"] = '%.8f' % quantity
        
        return params
           
    def _delete(self, path, params={}):
        params.update({"recvWindow": config.recv_window})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        header = {"X-MBX-APIKEY": self.key}
        return requests.delete(url, headers=header, \
            timeout=30, verify=True).json()

    def _format(self, price):
        return "{:.8f}".format(price)