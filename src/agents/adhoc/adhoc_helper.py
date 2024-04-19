from abc import ABC, abstractmethod


class AdhocHelper(ABC):

    @abstractmethod
    def give_helper_result(self, **kwargs):
        pass
