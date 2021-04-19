import urllib
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
import logging

logger = logging.getLogger("UcsmChassisFaultCollector")

class UcsmChassisFaultCollector(BaseCollector):
    def get_metrics(self):
        return {
            "faults": GaugeMetricFamily("ucsm_chassis_faults",
                                        "UCSM server chassis faults",
                                        labels=['server', 'fault',
                                                'severity', 'description'])
        }

    def collect_metrics(self, server, handle):
        g = self.get_metrics()['faults']

        sys = handle.query_dn("sys")
        chassis = self.query(handle.query_children, sys, class_id="EquipmentChassis")
        for chassi in chassis:
            faults = self.query(handle.query_children, chassi, class_id="FaultInst")
            logger.info("Faults ..... {0} - {1}".format(faults, server))
            if faults:
                for fault in faults:
                    g.add_metric(labels=[server, fault.cause, fault.severity, fault.descr],
                                    value=0)
        yield g
