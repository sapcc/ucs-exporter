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
            "fault": GaugeMetricFamily("ucsm_fault", "UCSM fault Status", labels=['server', 'type', 'description', 'dn', 'severity'])
        }

    def collect_metrics(self, server, handle):

        values = {
            "cleared": 0,
            "critical": 4,
            "major": 3,
            "warning": 2,
            "info": 1
        }

        g = self.get_metrics()['fault']

        faults = self.query(handle.query_classid, NamingId.FAULT_INST)

        if faults:
            for fault in faults:
                severity = values[fault.severity]
                # only add metrics for warning, major and critical for now
                if severity > 1:
                    g.add_metric(labels=[server, fault.type, fault.descr, fault.dn, fault.severity], value=severity)
        else:
            logger.info("{0}: No Faults detected.".format(server))

        yield g
