import json
import logging
import traceback
import urllib
from abc import ABC, abstractmethod
from prometheus_client.core import CounterMetricFamily
from ucsmsdk.ucsexception import UcsException
from .UcsmServer import UcsmServer

logger = logging.getLogger("BaseCollector")


class BaseCollector(ABC):
    def __init__(self, manager):
        self.manager = manager
        self.metrics = self.get_metrics()
        self._last_results = {}

    def get_handles(self):
        """yields all available connections as (server, handle) tuples"""
        for k, v in self.manager.get_handles().items():
            yield (k,v)

    def query(self, fnc, *args, **kwargs):
        for retry in range(2):
            try:
                return fnc(*tuple(args), **dict(kwargs))
            except urllib.error.URLError as e:
                logger.error(f"URLError: { e.reason }")
            except UcsException as e:
                if e.error_code == 552:
                    logger.info(f"Session timeout UCS: { e }. Retry # { retry }")
                    # we need to login again
                    if hasattr(fnc, "__self__") and hasattr(fnc.__self__, "login"):
                        fnc.__self__.logout()
                        fnc.__self__.login()
                    else:
                        logger.warning("Could not determin login function for refresh.")
                else:
                    logger.error(f"UCSException while query UCS: { e }. Retry: { retry }")
            except Exception as e:
                logger.exception(f"Exception while query UCS: { e }. Retry: { retry }")
            else:
                # data handler yielded without problems
                return ()
        return ()

    def collect(self):
        """Default implementation returns the last collected metrics"""
        # we report metrics only once
        for host, results in self._last_results.items():
            while len(results):
                yield results.pop(0)

    def update_cache(self, host):
        """Updates internal cache with latest query from servers"""
        new_data = []
        handle = self.manager.get_handle(host)
        if not handle:
            logger.info(f"Empty handle for server { host }")
        else:     
            for metric in self.collect_metrics(host, handle):
                new_data.append(metric)

        self._last_results[host] = new_data

    @abstractmethod
    def collect_metrics(self, host, handle):
        """Actual implementation that queries remote servers for metrics"""
        raise NotImplementedError

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

    def collect_metrics(self, server, handle):
        logger.debug(f"{ self.__class__.__name__ }.collect()")
        self.get_handles()
        mtr = self.get_metrics()

        for port in self.query(handle.query_classid, self.CLASS):
            port_name = port.dn
            for key in self.KEYS:
                if hasattr(port, key):
                    labels = [server, port_name]
                    mtr[key].add_metric(labels=labels, value=getattr(port, key))

        for m in mtr.values():
            yield m

