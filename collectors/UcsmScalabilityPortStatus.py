import urllib
import logging
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.ucsexception import UcsException


logger = logging.getLogger("UcsmScalabilityPortCollector")


class UcsmScalabilityPortStatus(BaseCollector):
    def __init__(self, manager):
        super().__init__(manager)
        self.admin_state = {
            "disabled": 0,
            "enabled": 1
        }

    def get_metrics(self):
        return {"scalability": GaugeMetricFamily("ucsm_scalability_port_status",
                                         "UCSM scalability port status",
                                         labels=['server', 'port', 'status'])
                                         }

    def collect_metrics(self, server, handle):
        logger.debug("Collecting Metrics ")
        g = self.get_metrics()['scalability']

        ports = self.query(handle.query_classid, "FabricEthLanPcEp")
        for port in ports:
            g.add_metric(labels=[server, port.dn, port.admin_state],
                            value=self.admin_state[port.admin_state])
        yield g

