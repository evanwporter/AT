# from .event import OrderEvent, FillEvent
from Broker.orders import *
from Broker.Fees import SlippageModel, PercentFeeModel

from collections import deque

from decimal import Decimal as D

import numpy as np

import datetime

import logging

# import enums
import helper as h
import settings


class SimulateExecutionHandler:
    def __init__(self, portfolio, dh):
        self.portfolio = portfolio
        self.dh = dh

        self.slippage = SlippageModel(dh)
        self.fee_model = PercentFeeModel()

        self.orders = {symbol: [] for symbol in dh.symbols}

    def on_order(
        self,
        id_,
        symbol,
        order_type,
        quantity,
        direction,
        fill_type="SIGNAL",
        price=None,
        profit_point=None,
        stop_loss=None,
    ):
        if order_type == "MARKET":

            if not settings.QUIET:
                print("Order Executed:", symbol, quantity, direction)

            commission, quantity = (
                0.01,
                0.01,
            )  # self.fee_model(price=price, quantity=quantity, broker=self)

            self.portfolio.on_fill(
                id_=id_,
                symbol=symbol,
                price=price,
                # exchange=symbol.source,
                fill_type=fill_type,
                quantity=quantity,
                direction=direction,
                commission=commission,
                slippage=self.slippage(symbol, price),
                stop_loss=stop_loss,
            )

        elif order_type == "STOP":
            side = h.reverse_side(direction)

            self.orders[symbol].append(
                StopOrder(id_=id_, quantity=quantity, stop_loss=stop_loss, side=side)
            )

        elif order_type == "TRAILING STOP":
            side = h.reverse_side(direction)

            self.orders[symbol].append(
                TrailingStopOrder(
                    id_=id_, quantity=quantity, stop_loss=stop_loss, side=side
                )
            )

        elif order_type == "TAKE PROFIT":
            side = h.reverse_side(direction)

            self.orders[symbol].append(
                TakeProfitOrder(
                    id_=id_, quantity=quantity, profit_point=profit_point, side=side
                )
            )

    def modify_order(self, symbol, order_id, quantity):
        orders = h.find_id(self.orders[symbol], order_id)
        if type(orders) == str:
            if quantity == 0:
                self.orders[symbol].remove(orders)
            else:
                self.orders[symbol][
                    self.orders[symbol].index(orders)
                ].quantity = quantity
        else:  # type(orders) == list
            for order in orders:
                if quantity == 0:
                    self.orders[symbol].remove(order)
                else:
                    self.orders[symbol][
                        self.orders[symbol].index(order)
                    ].quantity = quantity

    def check_orders(self, event):
        for symbol in event.symbols:
            date = self.dh.date
            price = self.dh.get_latest_data(symbol, "Close")

            for order in self.orders[symbol]:
                if isinstance(order, StopOrder):
                    if price < order.stop_loss:
                        self.on_order(
                            date=date,
                            id_=order.id_,
                            symbol=symbol,
                            order_type="MARKET",
                            fill_type="STOP",
                            price=order.stop_loss,
                            quantity=order.quantity,
                            direction=enums.trade_type.SELL,
                        )
                        self.orders[symbol].remove(order)
                        if settings.TAKE_PROFITS:
                            tp_order = h.find_id(self.orders[symbol], order.id_)
                            self.orders[symbol].remove(tp_order)

                elif isinstance(order, TrailingStopOrder):
                    prices = self.dh.get_latest_data(symbol, "Close", 2)

                    if price < order.stop_loss:
                        self.on_order(
                            date=date,
                            id_=order.id_,
                            symbol=symbol,
                            order_type="MARKET",
                            fill_type="STOP",
                            price=order.stop_loss,
                            quantity=order.quantity,
                            direction=enums.trade_type.SELL,
                        )
                        self.orders[symbol].remove(order)
                        if settings.TAKE_PROFITS:
                            tp_order = h.find_id(self.orders[symbol], order.id_)
                            self.orders[symbol].remove(tp_order)

                    elif prices[0] < price:
                        order.stop_loss += price - prices[0]

                elif isinstance(order, TakeProfitOrder):
                    if order.profit_point < price:
                        self.on_order(
                            date=date,
                            id_=order.id_,
                            symbol=symbol,
                            order_type="MARKET",
                            fill_type="PROFIT",
                            price=order.profit_point,
                            quantity=order.quantity,
                            direction=enums.trade_type.SELL,
                        )
                        self.orders[symbol].remove(order)

                        if settings.STOP_LOSSES:
                            sl_order = h.find_id(self.orders[symbol], order.id_)
                            self.orders[symbol].remove(sl_order)
