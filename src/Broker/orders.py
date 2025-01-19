from dataclasses import dataclass, field
from enums import side


@dataclass
class StopOrder:
    id_: str
    quantity: float
    stop_loss: float
    side: side


class TrailingStopOrder:
    def __init__(self, id_: str, quantity: float, stop_loss: float, side: side):
        self.id_ = id_
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.initial_stop_loss = stop_loss
        self.side = side


@dataclass
class TakeProfitOrder:
    id_: str
    quantity: float
    profit_point: float
    side: side
