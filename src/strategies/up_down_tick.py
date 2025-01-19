from strategies import Strategy


class UpDownTick(Strategy):
    """
    Super simple strategy. If the paramenter is set to TREND the if the
    stock goes up then it sends a LONG signal, if it goes down then it
    send a SHORT signal.

    The opposite happens if the parameter is set to MR or mean reversion.
    """

    type_ = "BAR"

    def __init__(self, method="TREND"):
        self.method = method

    def on_bar(self):
        data = self.dh.get_latest_data(self.symbol, N=2)

        if self.method == "TREND":
            if data[0] < data[1]:
                return "LONG"
            if data[0] > data[1]:
                return "SHORT"
        elif self.method == "MR":
            if data[0] > data[1]:
                return "SHORT"
            elif data[0] < data[1]:
                return "LONG"
