from abc import ABC, abstractmethod

from decimal import Decimal as D

from exceptions import *


class Strategy(ABC):
    def initialize(self, dh, rh):
        self.dh = dh
        self.symbols = self.dh.symbols

        self.rh = rh

        self.symbol = None

    def on_data(self, events):
        for event in events:
            if event.symbols:
                for symbol in event.symbols:
                    self.symbol = symbol

                    direction = getattr(self, "on_{}".format(event.type_.lower()))()

                    if direction is not None:
                        self.rh.on_signal(
                            symbol=symbol,
                            direction=direction,
                            price=self.close,
                        )

    @property
    def open(self):
        return self.dh.get_latest_data(self.symbol, columns="Open")

    @property
    def close(self):
        return self.dh.get_latest_data(self.symbol, columns="Close")

    @property
    def high(self):
        return self.dh.get_latest_data(self.symbol, columns="High")

    @property
    def low(self):
        return self.dh.get_latest_data(self.symbol, columns="Low")

    @property
    def volume(self):
        return self.dh.get_latest_data(self.symbol, columns="Volume")

    def on_bar(self, event):
        return None

    def on_sentiment(self, event):
        return None
