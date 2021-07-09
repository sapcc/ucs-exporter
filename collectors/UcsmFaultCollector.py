import urllib
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.ucsexception import UcsException
import logging

logger = logging.getLogger("UcsmFaultCollector")


class UcsmVIFCollector(BaseCollector):
    def get_metrics(self):
        return {
            "fault": GaugeMetricFamily("ucsm_fault", "UCSM fault Status", labels=['server', 'type', 'description', 'dn'])
        }

    def collect_metrics(self, server, handle):

        values = {
            "major": 1,
            "warning": 2,
            "info": 3
        }

        g = self.get_metrics()['fault']

        fault_inst = self.query(handle.query_classid, NamingId.FAULT_INST)

        for fault in fault_inst:
            severity = values[fault.severity]
            # only add metrics for warning and major for now
            if severity < 3:
                g.add_metric(labels=[server, fault.type, fault.descr, fault.dn], value=severity)

        yield g
