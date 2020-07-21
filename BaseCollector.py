from abc import ABC, abstractmethod


class BaseCollector(ABC):
    @abstractmethod
    def describe(self):
        pass

    @abstractmethod
    def collect(self):
        pass