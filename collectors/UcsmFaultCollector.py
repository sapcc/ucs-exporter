import urllib
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.ucsexception import UcsException
import logging

logger = logging.getLogger("UcsmFaultCollector")


class UcsmFaultCollector(BaseCollector):
    def get_metrics(self):
        return {
            "fault": GaugeMetricFamily("ucsm_faults", "UCSM fault Status", labels=['server', 'type', 'description', 'dn', 'severity'])
        }

    def collect_metrics(self, server, handle):

        g = self.get_metrics()['fault']

        faults = self.query(handle.query_classid, NamingId.FAULT_INST)

        if faults:
            for fault in faults:
                logger.info("{0}: UCSM fault detected with severity {1}".format(server, fault.severity))
                g.add_metric(labels=[server, fault.type, fault.descr, fault.dn, fault.severity], value=1)
        else:
            logger.info("{0}: No UCSM faults detected.".format(server))
            g.add_metric(labels=[server], value=0)

        yield g
