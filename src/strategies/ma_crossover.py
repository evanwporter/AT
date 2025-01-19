class MovingAverageCrossover:
    type_ = "BAR"

    def __init__(self, window):
        self.window = window

    def on_bar(self):
        data = self.dh.get_latest_data(self.symbol, N=self.window)

        self.price = data[-1]

        if data is not None and len(data) >= self.window:
            # Not really moving lol
            average = np.mean(data)

            if price > average:
                return "LONG"
            elif price < average:
                return "SHORT"
