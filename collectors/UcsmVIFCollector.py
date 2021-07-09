import urllib
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.ucsexception import UcsException
import logging

logger = logging.getLogger("UcsmVICCollector")


class UcsmVIFCollector(BaseCollector):
    def get_metrics(self):
        return {
            "vif": GaugeMetricFamily("ucsm_vif_link", "UCSM server VIF Link Status", labels=['server', 'port'])
        }

    def collect_metrics(self, server, handle):
        values = {
            "up": 1, 
            "down": 0, 
            "offline":2, 
            "unknown": -1
        }

        g = self.get_metrics()['vif']

        interfaces = self.query(handle.query_classid, NamingId.DCX_VC)
        for interface in interfaces:
            g.add_metric(labels=[server, interface.dn], value=values[interface.link_state])

        yield g
