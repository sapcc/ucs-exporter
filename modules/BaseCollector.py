import json
import logging
from abc import ABC, abstractmethod
from ucsmsdk.ucsexception import UcsException
from .UcsmServer import UcsmServer

logger = logging.getLogger("BaseCollector")


class BaseCollector(ABC):
    def __init__(self, manager):
        self.manager = manager

    def get_handles(self):
        return self.manager.get_handles()
    @property
    def handles(self):
        return self.manager.handles

    @abstractmethod
    def describe(self):
        pass

    @abstractmethod
    def collect(self):
        pass
