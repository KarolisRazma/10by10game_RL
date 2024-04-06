from abc import ABC, abstractmethod


class AdhocStrategy(ABC):

    @abstractmethod
    def give_strategy_result(self, **kwargs):
        pass
