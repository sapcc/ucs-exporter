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
        self.metrics = self.get_metrics()
        self._last_results = []

    def get_handles(self):
        return self.manager.get_handles()

    def query(self, fnc, *args, **kwargs):
        for retry in range(2):
            try:
                return fnc(*args, **kwargs)
            except urllib.error.URLError as e:
                logger.error("URLError: ", server, e.reason)
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
    
    def collect(self):
        """Default implementation returns the last collected metrics"""
        for m in self._last_results:
            yield m

    def update_cache(self):
        """Updates internal cache with latest query from servers"""
        new_data = []
        for metric in self.collect_metrics():
            new_data.append(metric)

        self._last_results = new_data

    @abstractmethod
    def collect_metrics(self):
        """Actual implementation that queries remote servers for metrics"""
        pass

    @abstractmethod
    def get_metrics(self):
        """Returns a dict of metrics this collector returns"""
        pass

    def describe(self):
        metrics = self.get_metrics()
        for m in metrics.values():
            yield m


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

    def collect_metrics(self):
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

