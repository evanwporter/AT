from collections import deque, defaultdict

from strategies import Strategy


class CombinedStrategies(Strategy):
    def __init__(self, method="all", **kwargs):
        """[summary]

        Parameters
        ----------
        method : str
        kwargs : variable/list
            Where the key is the name of the strategy
            and the value are the parameters to pass
            to the strategy.
        """
        self.method = method
        self.kwargs = kwargs

    def initialize(self, dh, rh):
        super().initialize(dh, rh)

        self.strategies = defaultdict(list)
        for strategy, parameters in self.kwargs.items():
            # Instantaniate strategy class
            strategy = getattr(Strategies, strategy)(*parameters)
            strategy.initialize(self.dh, self.rh)
            self.strategies[strategy.type_].append(strategy)

    def on_data(self, events):
        directions = []
        for event in events:
            if event.symbols:
                for symbol in event.symbols:
                    for strategy in self.strategies[event.type_]:
                        self.symbol = symbol
                        strategy.symbol = symbol

                        direction = getattr(
                            strategy, "on_{}".format(event.type_.lower())
                        )()

                        if direction == "LONG":
                            directions.append(1)
                        elif direction == "SHORT":
                            directions.append(-1)
                        else:
                            directions.append(0)

        direction = None
        if self.method == "any":
            if sum(directions) >= 1:
                direction = "LONG"
            elif sum(directions) <= 1:
                direction = "SHORT"
        elif self.method == "all":
            if sum(directions) == len(directions):
                direction = "LONG"
            elif sum(directions) == len(directions):
                direction = "SHORT"

        if direction is not None:
            self.rh.on_signal(
                date=event.date,
                symbol=self.symbol,
                direction=direction,
                price=self.close,
            )

    def calculate_signals(self, event):
        direction = 0
        signal = None
        for strategy in self.strategies.values():
            strategy.calculate_signals(event)
            try:
                signal = self.local_events.popleft()
                if signal.signal_type == "LONG" and direction != -1:
                    direction = 1
                elif signal.signal_type == "SHORT" and direction != 1:
                    direction = -1
                else:
                    break
            except IndexError:
                continue
        else:
            if signal is not None:
                self.events.append(signal)
