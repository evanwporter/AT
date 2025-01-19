import numpy as np
from decimal import Decimal as D

import helper as h

import logging

try:
    import talib
except ImportError:
    # talib is a pain to install
    logging.warning("You should install talib.")

import enums

import settings

from Broker.Fees import PercentFeeModel

import helper as h

# TODO:
#  * Reincoporate hrp allocation
#  * Add more position size techniques
#     * Kelly Criterion
#     * Van Tharp CPR


class SimpleRiskHandler:
    def __init__(
        self,
        dh,
        portfolio,
        broker,
        weighting="long only",
    ):
        self.dh = dh

        self.portfolio = portfolio
        self.holdings = self.portfolio.holdings
        self.positions = self.portfolio.positions

        self.broker = broker
        self.fee_model = PercentFeeModel()

        # Maximum Leverage Ratio
        self.MLR = settings.LEVERAGE_RATIO
        if self.MLR is not type(D):
            self.MLR = D(self.MLR)

        # Cash Buffer
        self.CB = D(settings.CASH_BUFFER) * D(settings.INITIAL_CASH)
        if self.CB == D("0"):
            logging.warning(
                "Cash buffer is 0. The recommended cash buffer is at least .05"
            )

        try:
            cash_buffer = int(settings.CASH_BUFFER * 100)
        except:
            cash_buffer = 0.2
            logging.warning("You should define settings.CASH_BUFFER")

        try:
            self.weight_bounds = settings.WEIGHTS
        except ValueError:  # If WEIGHTS isn't defined in settings
            self.weight_bounds = {}
            logging.warning("You should define settings.WEIGHTS")

        # TODO: Seperate into cash like and not cash like lists
        # Then divide available weightings evenly
        # Also incorporate Long Only setting

        # Check if its empty
        if self.weight_bounds:
            not_cash_like_weight = (1 - cash_buffer) / len(
                [s for s in self.dh.split_symbols if not h.is_cash_like(s)]
            )
            for s in self.dh.split_symbols:
                # TODO: Currently this will break if there are more than 1 cash like assets
                if h.is_cash_like(s):
                    self.weight_bounds[s] = (cash_buffer, 100)
                else:
                    self.weight_bounds[s] = (0, not_cash_like_weight)

        # for weight in self.weight_bounds

        # Current Weights
        self.weights = self.portfolio.weights

        #         self.weighting = settings.WEIGHTING

        logging.info("Weight Bounds: %s" % self.weight_bounds)

    # def _allocate_cash_buffer(self):
    #     cash_buffer = self.CB * self.total_equity
    #     available_cash = self.portfolio.cash.quantity - cash_buffer
    #     for order in self.broker.orders:
    #         commission

    def _bet_size(self, price):
        # name = settings.POSITION_SIZER["method"]

        # # if name == r"Fixed % TE":
        # #     quantity = (settings.POSITION_SIZER["size"] * self.TE) / price

        # # if name == "Fixed Size":
        # #     quantity = settings.POSITION_SIZER["size"]

        # # if quantity is not type(D):
        # #     quantity = D(quantity)

        return D(".05")

    def _calculate_direction(self, symbol, quantity, direct):
        """There are two kinds of orders orders that increase a position
        (Long and Short orders) and orders that decrease a position (Buy
        and Sell).

        Parameters
        ----------
        symbol : str
        """

        current_position = self.positions[symbol].quantity
        if direct == "LONG":
            if quantity + current_position > 0:
                direction = "LONG"
            else:  # quantity + self.positions[event.symbol].quantity <= 0:
                # Buy orders happen only if a position is negative
                # Meaning its been shorted
                direction = "BUY"
        else:
            # Been shorted
            if -quantity + current_position < 0:
                direction = "SHORT"
            else:  # quantity + self.positions[event.symbol].quantity >= 0:
                direction = "SELL"

        return direction

    def _adjust_for_commission(self, quantity, price):
        # TODO: Expand to allow for other exchanges
        return ((quantity * price) / (1 + settings.FEES["Binance"])) / price

    def _check_leverage(self, price, direction, symbol):
        """
        This function is mostly obsolete, as its been replaced by _check_weights().
        """

        current_holdings = self.holdings[-1]

        if direction == "SHORT" or direction == "SELL":
            quantity = -self.quantity

        # Maximum Asset Value
        MAV = self.MLR * self.TE

        # Usable Asset Value
        # TODO: Implement some algorithm for calculating the way back
        UAV = MAV - (
            current_holdings["Assets"]
            - ((current_holdings["Cash"] * D(".999")))
            - self.CB
        )

        # Maximum Quantity
        MQ = UAV / price

        if self.quantity > MQ:
            self.quantity = MQ

        # mock_holding = self.holdings[-1].copy()

        # # Market Value
        # MV = price * self.quantity

        # try:
        #     mock_holding["%s Value" % symbol] += MV
        # except KeyError:
        #     mock_holding["%s Value" % symbol] = MV

        # mock_holding["Cash"] -= MV * .999
        # mock_holding_array = np.array(list(mock_holding.values())[:-4])

        # # Potential Asset Value
        # PAV = np.sum(mock_holding_array[mock_holding_array > 0])

        # TE = np.sum(mock_holding_array)

        # # Potential Leverage Ratio
        # PLR = PAV / TE

        # if self.MLR < PLR:
        #     self.quantity = 0

        # PLR = self.MLR

        # # Adjusted AV
        # AAV = PLR * TE

        # market_value = AAV - self.holdings[-1]["Assets"]

        # self.quantity = round(
        #     market_value / price, 8
        # )

    def _set_stop_loss(self, symbol, price, direction, date, id_):
        data = self.dh.get_latest_data(
            symbol, columns=["Close", "High", "Low"], N=0, dtype=np.float64
        )
        volatility = D((3 * talib.ATR(*data))[-1])

        if direction == enums.trade_type.LONG:
            stop_loss = price - volatility
        elif enums.trade_type.SHORT:
            stop_loss = price + volatility

        self.broker.on_order(
            date=date,
            id_=id_,
            symbol=symbol,
            stop_loss=stop_loss,
            order_type="TRAILING STOP",
            quantity=self.quantity,
            direction=direction,
        )

        return stop_loss

    def _set_take_profit(self, symbol, price, direction, date, id_):
        data = self.dh.get_latest_data(
            symbol, columns=["Close", "High", "Low"], N=0, dtype=np.float64
        )
        volatility = D((0.5 * talib.ATR(*data))[-1])

        if direction == enums.trade_type.LONG:
            profit_point = price + volatility
        elif enums.trade_type.SHORT:
            profit_point = price - volatility

        self.broker.on_order(
            date=date,
            id_=id_,
            symbol=symbol,
            profit_point=profit_point,
            order_type="TAKE PROFIT",
            quantity=self.quantity,
            direction=direction,
        )

        return profit_point

    def _check_weights(
        self, base, quote, weight_adjustment, price, direction, debug=False
    ):

        # The weights are how much of the Total Equity are in a particular asset
        # Weight bounds are predefined maximum weights for each asset
        # This function checks to see if the proposed trade will go over
        # or under the weight bounds

        weight_adjustment = weight_adjustment * 100

        # Current weights
        base_weight = self.weights[base]
        quote_weight = self.weights[quote]

        # Weight Bounds
        base_min_weight, base_max_weight = self.weight_bounds[base]
        quote_min_weight, quote_max_weight = self.weight_bounds[quote]

        if direction == "LONG":
            # Buy/Long means increase `Base Asset` and decrease `Quote Asset`
            distance = min(
                quote_weight - quote_min_weight,  # Quote distance
                base_max_weight - base_weight,  # Base distance
            )
            if distance < weight_adjustment:
                # Scales quanity down
                weight_adjustment = distance

        elif direction == "SHORT":
            # Sell/Short means decrease Base and increase Quote
            _adjust_for
            quote_distance = quote_max_weight - quote_weight
            base_distance = base_weight - base_min_weight

            distance = min(quote_distance, base_distance)

            if distance < weight_adjustment:
                # Scales quantity up
                weight_adjustment = distance

        # Turn the weight adjustment into a hard quantity
        quantity = (self.TE * weight_adjustment) / (price * 100)

        return self._adjust_for_commission(quantity=quantity, price=price).quantize(
            D(enums.places.EIGHT)
        )

    def on_signal(self, price, symbol, direction):
        base = symbol.base
        quote = symbol.quote

        self.TE = self.portfolio.total_equity

        weight_adjustment = self._bet_size(price)
        quantity = self._check_weights(
            base=base,
            quote=quote,
            weight_adjustment=weight_adjustment,
            price=price,
            direction=direction,
        )

        direction = self._calculate_direction(base, quantity, direction)

        # if direction == "SHORT":
        #     weight = self.weights["Binance-BTC"]
        #     self._check_weights(
        #         base=base,
        #         quote=quote,
        #         weight_adjustment=weight_adjustment,
        #         price=price,
        #         direction=direction,
        #         debug=True,
        #     )

        if quantity > 0:
            id_ = h.generate_unique_id()

            if direction == "LONG" or direction == "SHORT":
                stop_loss = (
                    self._set_stop_loss(symbol, price, direction, date, id_)
                    if settings.STOP_LOSSES
                    else None
                )
                profit_point = (
                    self._set_take_profit(symbol, price, direction, date, id_)
                    if settings.TAKE_PROFITS
                    else None
                )

            else:
                stop_loss = None
                profit_point = None

            self.broker.on_order(
                id_=id_,
                symbol=symbol,
                price=price,
                order_type="MARKET",
                quantity=quantity,
                direction=direction,
                stop_loss=stop_loss,
                profit_point=profit_point,
            )
