from decimal import Decimal as D
import logging
import helper as h


class SuperSimpleRiskHandler:
    def __init__(
        self,
        portfolio,
        broker,
        max_allocation=0.1,
        stop_loss_pct=0.05,
        take_profit_pct=0.1,
    ):
        """
        Initialize the risk handler for stocks.

        Args:
            portfolio: Portfolio object managing current holdings.
            broker: Broker object handling order execution.
            max_allocation (float): Maximum fraction of total portfolio equity to allocate to a single stock.
            stop_loss_pct (float): Stop loss percentage (e.g., 0.05 for 5% below entry price).
            take_profit_pct (float): Take profit percentage (e.g., 0.1 for 10% above entry price).
        """
        self.portfolio = portfolio
        self.broker = broker
        self.max_allocation = D(max_allocation)
        self.stop_loss_pct = D(stop_loss_pct)
        self.take_profit_pct = D(take_profit_pct)

        logging.info(
            f"Risk Handler initialized with max_allocation={max_allocation}, "
            f"stop_loss_pct={stop_loss_pct}, take_profit_pct={take_profit_pct}"
        )

    def calculate_quantity(self, price, total_equity):
        """
        Calculate the number of shares to buy based on the price and maximum allocation.

        Args:
            price (Decimal): Current price of the stock.
            total_equity (Decimal): Total portfolio equity.

        Returns:
            Decimal: Number of shares to purchase.
        """
        allocation = self.max_allocation * total_equity
        quantity = allocation // price
        logging.info(
            f"Calculated quantity: {quantity} for price: {price} and total equity: {total_equity}"
        )
        return quantity

    def place_order(self, symbol, price, direction, total_equity):
        """
        Place a market order with stop loss and take profit.

        Args:
            symbol (str): Stock ticker symbol.
            price (Decimal): Current price of the stock.
            direction (str): Direction of the trade ("BUY" or "SELL").
            total_equity (Decimal): Total portfolio equity.
        """
        # Calculate the number of shares to trade
        quantity = self.calculate_quantity(price, total_equity)

        if quantity == 0:
            logging.warning(f"Insufficient funds to place order for {symbol}")
            return

        # Calculate stop loss and take profit levels
        stop_loss = None
        take_profit = None

        if direction == "BUY":
            stop_loss = price * (1 - self.stop_loss_pct)
            take_profit = price * (1 + self.take_profit_pct)
        elif direction == "SELL":
            stop_loss = price * (1 + self.stop_loss_pct)
            take_profit = price * (1 - self.take_profit_pct)

        # Place order via broker
        self.broker.on_order(
            symbol=symbol,
            price=price,
            order_type="MARKET",
            quantity=quantity,
            direction=direction,
            stop_loss=stop_loss,
            id_=h.generate_unique_id(),
            # take_profit=take_profit,
        )

        logging.info(
            f"Order placed: {direction} {quantity} shares of {symbol} at {price} with "
            f"stop_loss={stop_loss}, take_profit={take_profit}"
        )

    def on_signal(self, symbol, price, direction):
        """
        Respond to a trade signal.

        Args:
            symbol (str): Stock ticker symbol.
            price (Decimal): Current price of the stock.
            direction (str): Direction of the trade ("BUY" or "SELL").
        """
        total_equity = self.portfolio.total_equity
        self.place_order(symbol, price, direction, total_equity)
