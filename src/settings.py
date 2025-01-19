"""
Settings Page
-------------
TODO
 * Documentation
"""

from decimal import Decimal as D

"""
There are three modes
 * Backtest `backtest`: Uses the `HistoricDataHandler` and the `SimulatedExecutionHandler`
 * Paper Trading `paper`: Uses the `LiveDataHandler` and the `SimulatedExecutionHandler`
 * Live Trader `live`: Uses the `LiveDataHandler` and the `ExchangeHandler`
"""
MODE = "backtest"

FEES = D(0.001)


# ---------------------
# | Symbol Parameters |
# ---------------------
DEFAULT = {"Data Interval": "1D", "Trading Interval": "1D"}

SYMBOLS = {
    # Symbols in exchange that you want to trade
    # Symbols must have a similarily named csv file
    "GOOG": DEFAULT,
    "AAPL": DEFAULT,
    "MSFT": DEFAULT,
}

DATA_INTERVAL = "1m"
TRADING_INTERVAL = "1m"

# ----------------
# | Data Handler |
# ----------------
# Warmup period is how many the starting point for the data. Everything in the
# warmup period can be used as data right from the start.
DATA_WARMUP_PERIOD = 500
DATA_DIRECTORY = r"C:\Users\evanw\AT\Data"

# ------------
# | Strategy |
# ------------

# Strategy you want to use. Backtesting uses getattr to read the strategy
# provided that their is a equivalently named strategy in the strategy folder.
STRATEGY = "UpDownTick"
PARAMETERS = {"method": "TREND"}

# ----------------
# | Risk Handler |
# ----------------
TAKE_PROFITS = False
STOP_LOSSES = False
LEVERAGE_RATIO = 1.0
# Percent of total equity
CASH_BUFFER = 0.2
WEIGHTING = "long-only"
POSITION_SIZER = {"method": "Fixed Size", "size": ".1"}
WEIGHTS = {symbol: 0.33 for symbol in SYMBOLS}

# -------------
# | Portfolio |
# -------------
INITIAL_CASH = 1000

# ----------
# | Broker |
# ----------
QUIET = True

# FEE MODEL
ADJUST_QUANTITY = True
SLIPPAGE_LAG = 1

BINANCE_PUBLIC = "#"
BINANCE_PRIVATE = "#"
