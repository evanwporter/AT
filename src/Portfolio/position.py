from decimal import Decimal as D
from collections import deque
from dataclasses import dataclass, field

# from .trade import Trade

from enums import trade_type, asset_side, places


@dataclass
class Position:

    # TWOPLACES = Decimal("0.01")
    # FIVEPLACES = Decimal("0.00001")

    symbol: str

    # 8 decimals to handle crypto
    quantity: D = D("0.0")

    # Realized P&L are the profits you've accumulated from the assets you've sold
    realized_pnl: D = field(init=False, default=D("0.0"))

    _avg_cpu: D = field(init=False, default=D("0.0"))

    # Cost basis is the original price you payed for an asset
    cost_basis: D = field(init=False, default=D("0.0"))

    total_commission: D = field(init=False, default=D("0.0"))
    total_slippage: D = field(init=False, default=D("0.0"))

    market_value: D = field(init=False, default=D("0.0"))

    def update_value(self, price, date=None):

        self.market_value = self.quantity * price  # .quantize(self.FIVEPLACES)

        # Unrealized P&L is how much profit you'll make if you sell at current market prices
        # self.unrealized_pnl = (self.market_value - self._avg_cpu * self.quantity)#.quantize(self.TWOPLACES)
        return self.market_value.quantize(D(places.EIGHT))

    def __dict__(self):
        return {
            "Symbol": self.symbol,
            "Quantity": self.quantity,
            "Market Value": self.market_value,
            # 'Realized P&L': self.realized_pnl,
            # 'Unrealized P&L': self.unrealized_pnl,
            # 'Cost Basis': self.cost_basis
        }

    def update_position(
        self,
        direction,
        quantity: D | int | str,
        price,
        side,
        commission: D | int | str = D("0.0"),
        slippage=None,
        date=None,
    ):

        if (not isinstance(quantity, D)) and (quantity is not None):
            quantity = D(quantity)

        if (not isinstance(commission, D)) and (commission is not None):
            commission = D(commission)

        # Adjusts for cash
        # asset_side.QUOTE == "Quote"
        if side == asset_side.QUOTE:
            self.quantity -= commission
            qp = quantity * price
            self.total_commission += commission

            if direction == "BUY" or direction == "LONG":
                self.quantity -= qp
            else:
                self.quantity += qp

        else:
            if direction == trade_type.LONG or direction == trade_type.BUY:

                # CPU is Cost Per Unit
                # Adjust average cost per unit
                # try:
                #     self._avg_cpu = ((self._avg_cpu * self.quantity + price * quantity) / (self.quantity + quantity))#.quantize(self.TWOPLACES)
                # except ZeroDivisionError: self._avg_cpu = 0.0
                self.quantity += quantity

                # self.cost_basis += price * quantity

            else:  # direction == "SELL"

                # self.realized_pnl += price * quantity - self._avg_cpu * quantity

                self.quantity -= quantity
