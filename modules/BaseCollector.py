import json
import logging
import traceback
from abc import ABC, abstractmethod
from prometheus_client.core import CounterMetricFamily
from ucsmsdk.ucsexception import UcsException
from .UcsmServer import UcsmServer

logger = logging.getLogger("BaseCollector")


class BaseCollector(ABC):
    def __init__(self, manager):
        self.manager = manager

    def get_handles(self):
        return self.manager.get_handles()

    def query(self, fnc, *args, **kwargs):
        for retry in range(2):
            try:
                return fnc(*args, **kwargs)
            except UcsException as e:
                if e.error_code == 552:
                    # we need to login again
                    handle.logout()
                    handle.login()
                else:
                    logger.error("UCSException while query UCS: %s. Retry: %s" % (e, retry))
            except Exception as e:
                logger.error("Exception while query UCS: %s. Retry: %s" % (e, retry))
                traceback.print_exc()
        return ()

    @property
    def handles(self):
        return self.manager.handles

    @abstractmethod
    def describe(self):
        pass

    @abstractmethod
    def collect(self):
        pass

class GenericClassCollector(BaseCollector):
    """
    Maps a list of query keys to CounterMetrics
    """
    def get_metrics(self):
        rv = {}
        for key in self.KEYS:
            rv[key] = CounterMetricFamily(self.PREFIX.format(key=key), self.DESCRIPTION.format(key=key),
                                          labels=self.LABELS)
        return rv

    def describe(self):
        metrics = self.get_metrics()
        for m in metrics.values():
            yield m

    def collect(self):
        logger.debug("%s.collect()" % self.__class__.__name__)
        self.get_handles()
        mtr = self.get_metrics()

        for server, handle in self.handles.items():
            for port in self.query(handle.query_classid, self.CLASS):
                port_name = port.dn
                for key in self.KEYS:
                    if hasattr(port, key):
                        labels = [server, port_name]
                        mtr[key].add_metric(labels=labels, value=getattr(port, key))

        for m in mtr.values():
            yield m

