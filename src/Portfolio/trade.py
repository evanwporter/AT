from dataclasses import dataclass, field
from pandas import Timestamp


class Trade:
    def __init__(
        self,
        symbol,
        id_,
        open_date,
        quantity,
        price,
        slippage,
        commission,
        direction,
        stop_loss=None,
    ):
        self.symbol: str = symbol
        self.id_: str = id_
        self.open_date: Timestamp = open_date
        self.quantity: float = quantity
        self.expected_price = price
        self.open_price: float = price - slippage
        self.slippage: float = slippage
        self.commission: float = commission
        self.direction: str = direction
        self.stop_loss: float = stop_loss
        self.close_date: Timestamp = None

    # close_price: float = field(init=False)