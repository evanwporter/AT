from dataclasses import dataclass, field
from typing import List
from pandas import Timestamp

import helper as h


class Event:
    pass


# @dataclass generates a bunch of nice things such as __init__ and __repr__
# https://docs.python.org/3/library/dataclasses.html


@dataclass
class MarketEvent(Event):
    type_: str = field(init=False, default="MARKET")
    symbols: List[dict] = field(init=False, default_factory=list)
    date: Timestamp


@dataclass
class SignalEvent(Event):
    type_: str = field(init=False, default="SIGNAL")
    date: Timestamp
    symbol: str
    price: float
    direction: str


# strength: int = 100


@dataclass
class OrderEvent(Event):
    type_: str = field(init=False, default="ORDER")
    id_: str = field(init=False, default=h.generate_unique_id())
    date: Timestamp
    symbol: str
    price: float
    order_type: str
    quantity: float
    direction: str
    stop_loss: float | None = None


@dataclass
class FillEvent(Event):
    type_: str = field(init=False, default="FILL")
    id_: str
    date: Timestamp
    symbol: str
    price: float
    exchange: str
    quantity: float
    direction: str
    commission: float | None = None
    stop_loss: float | None = None

    # def calculate_ib_commission(self):
    #     full_cost = 1.3
    #     if self.quantity <= 500:
    #         full_cost = max(1.3, 0.013 * self.quantity)
    #     else:
    #         full_cost = max(1.3, 0.008 * self.quantity)
    #     full_cost = min(full_cost, 0.5 / 100.0 * self.quantity * self.fill_cost)
    #     return full_cost
