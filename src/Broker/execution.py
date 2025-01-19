from abc import ABC, abstractmethod

class Broker(ABC):
    @abstractmethod
    def on_order(self):
        raise NotImplementedError("Should implement `on_order`")