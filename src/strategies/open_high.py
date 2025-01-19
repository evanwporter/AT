import pandas as pd
import numpy as np

from event import SignalEvent


class OpenHigh:
    def __init__(self, dh, events, period=9):
        self.dh = dh
        self.events = events
        self.period = period
        self.bought = {False for symbol in dh.symbols}

    def calculate_signals(self, event):
        symbol = event.symbol

        data = pd.DataFrame(
            self.dh.get_latest_data(symbol, self.period),
            columns=self.dh.symbols[symbol]["Columns"].keys(),
        )

        data["Open-High Diff"] = price_diff = (data["High"] - data["Open"]) / data[
            "Open"
        ].shift()

        price = data["Open"].iloc[-1]
        current_diff = data["Open-High Diff"].iloc[-1]

        # Lag the data so lookahead bias doesn't occur
        data = data[:-1]

        avg_oh_diff = price_diff.mean() * 9 / 10

        self.events.append(
            SignalEvent(
                symbol=symbol,
                date=event.date,
                price=price,
                signal_type="LONG",
                idx=event.index,
                strength=100,
            )
        )

        if current_diff > avg_oh_diff:
            self.events.append(
                SignalEvent(
                    symbol=symbol,
                    date=event.date,
                    price=(avg_oh_diff + 1)
                    * event.bar[self.dh.symbols[symbol]["Columns"]["Open"]],
                    signal_type="SHORT",
                    strength="all",
                    idx=event.index,
                )
            )
