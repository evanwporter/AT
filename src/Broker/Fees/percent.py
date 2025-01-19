from .fee import FeeModel
from enums import exchanges, places

import settings

from decimal import Decimal as D


class PercentFeeModel:
    def __init__(self):
        self.adjust_quantity = settings.ADJUST_QUANTITY
        self.broker_fees = settings.FEES

    def _calculate_commission(self, consideration, broker):
        return self.broker_fees[broker] * consideration

    def _commission_adjusted_quantity(self, consideration, q, p, broker):
        """
        You have $1000. You want to spend all $1000 on Asset A.
        Your model tells you to purchase 10 of Asset A for $100 each.
        The issue is that if you follow your models recommendation
        without taking into account commissions (and slippage) you
        will be forced to go into debt or your broker will simply
        not execute the order as you lack the necessary money.

        Given:
            consideration = qpc + qp
        Thus:
            q = (consideration) / ((c + 1) * p)
        (where c is commission)

        Keep in mind that this only works for assets with a
        divisible quantity (ie: crypto)

        Parameters
        ----------
        consideration : float
            p * q
        q : float
            Quantity
        p : float
            Price
        broker : str

        Returns
        -------
        float
            Commission adjusted quantity
        """
        return consideration / (
            (self.broker_fees[broker] + D("1")) * p
        )  # .quantize(D(places.EIGHT))

    def __call__(self, quantity, price, broker=exchanges.BINANCE):
        consideration = quantity * price
        commission = self._calculate_commission(consideration, broker)

        if self.adjust_quantity:
            adjusted_quantity = self._commission_adjusted_quantity(
                consideration, q=quantity, p=price, broker=broker
            )
        else:
            adjusted_quantity = quantity

        return commission, adjusted_quantity
