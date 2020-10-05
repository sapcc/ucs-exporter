from prometheus_client.core import CounterMetricFamily
from ucsmsdk.ucsconstants import NamingId
from BaseCollector import BaseCollector
import logging
logger = logging.getLogger("UcsPortErrStatsCollector")


class UcsPortErrStatsCollector(BaseCollector):
    KEYS = ['align', 'deferred_tx', 'fcs', 'int_mac_rx', 'int_mac_tx', 'out_discard', 'rcv', 'under_size', 'xmit']

    def get_metrics(self):
        rv = {}
        for key in self.KEYS:
            rv[key] = CounterMetricFamily('ucs_port_err_%s' % key, 'Error counter for statistic %s' % key,
                                          labels=['server', 'port_name'])
        return rv

    def describe(self):
        metrics = self.get_metrics()
        for m in metrics.values():
            yield m

    def collect(self):
        logger.debug("UcsPortErrStatsCollector.collect()")
        self.get_handles()
        mtr = self.get_metrics()

        for server, handle in self.handles.items():
            for port in handle.query_classid(NamingId.ETHER_ERR_STATS):
                port_name = port.dn
                for key in self.KEYS:
                    labels = [server, port_name]
                    mtr[key].add_metric(labels=labels, value=getattr(port, key, 0))

        for m in mtr.values():
            yield m
