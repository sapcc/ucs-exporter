import urllib
import logging
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector


logger = logging.getLogger("UcsmChassisCollector")


class UcsmChassisFaultCollector(BaseCollector):
    def get_metrics(self):
        return {
            "faults": GaugeMetricFamily("ucsm_chassis_faults",
                                        "UCSM server chassis faults",
                                        labels=['server', 'fault',
                                                'severity', 'description'])
        }

    def collect_metrics(self, server, handle):
        logger.info("Collecting Metrics ")
        g = self.get_metrics()['faults']

        sys = handle.query_dn("sys")
        chassis = self.query(handle.query_children, sys, class_id="EquipmentChassis")
        for chassi in chassis:
            faults = self.query(handle.query_children, chassi, class_id="FaultInst")
            logger.debug("Faults : %s %s", faults, server)
            if faults:
                for fault in faults:
                    g.add_metric(labels=[server, fault.cause, fault.severity, fault.descr],
                                    value=0)
        yield g
