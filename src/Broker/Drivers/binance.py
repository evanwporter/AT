import enums
import settings
import exceptions
import time
import hashlib
import requests
import hmac
from urllib.parse import urlencode


class Binance:
    private = settings.BINANCE_PRIVATE
    public = settings.BINANCE_PUBLIC
    BASE_URL_V3 = "https://api.binance.com/api/v3"

    def order(self, symbol: str, side: str, type_: str, **kwargs):
        limit_order_reqs = ("timeInForce", "quantity", "price")
        market_order_reqs = ("quantity", "quoteOrderQty")
        sl_order_reqs = ("quantity", "stopPrice")
        tp_order_reqs = ("quantity", "stopPrice")

        if type_ == "LIMIT" and not all(
            parameter in kwargs for parameter in limit_order_reqs
        ):
            raise ValueError()
        elif type_ == "MARKET" and not any(
            parameter in kwargs for parameter in market_order_reqs
        ):
            raise ValueError()
        elif type_ == "STOP_LOSS" and not all(
            parameter in kwargs for parameter in sl_order_reqs
        ):
            raise ValueError()
        elif type_ == "TAKE_PROFIT" and not all(
            parameter in kwargs for parameter in tp_order_reqs
        ):
            raise ValueError()

        kwargs.update({"symbol": symbol, "side": side, "type": type_})

        self._post()

    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})

        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(
            b, msg=h.encode("utf-8"), digestmod=hashlib.sha256
        ).hexdigest()
        data.update({"signature": signature})

        return data

    def _post(self, path, params={}):
        # params.update({"recvWindow": config.recv_window})
        query = urlencode(self._sign(params))
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(
            url, headers=header, data=query, timeout=30, verify=True
        ).json()


client = Binance()
client.order("BTC", "BUY", "TYPE", peace="peace")
