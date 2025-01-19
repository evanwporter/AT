from abc import ABC, abstractmethod


class FeeModel(ABC):
    @abstractmethod
    def _calc_commission(self, consideration, broker=None):
        raise NotImplementedError("Should implement _calc_commission()")

    @abstractmethod
    def calc_total_cost(self, consideration, broker=None):
        # raise NotImplementedError("Should implement calc_total_cost()")
        pass

