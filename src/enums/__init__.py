class side:
    BUY = "BUY"
    SELL = "SELL"


class trade_type:
    LONG = "LONG"
    SHORT = "SHORT"
    BUY = "BUY"
    SELL = "SELL"

class order_type:
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT	= "STOP_LOSS_LIMIT"
    TAKE_PROFIT	= "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"
    LIMIT_MAKER = "LIMIT_MAKER"


class exchanges:
    BINANCE = "Binance"
    BINANCE_US = "BinanceUS"


class time_in_force:
    GTC = "GTC"  # Good til cancel
    IOC = "IOC"  # Immediate or cancel
    FOK = "FOK"  # Fill or kill

class places:
    EIGHT = "0.00000000"

class asset_side:
    QUOTE = "Quote"
    BASE = "Base"