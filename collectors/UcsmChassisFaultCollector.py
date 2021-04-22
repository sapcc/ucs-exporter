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
                                        labels=['server', 'chassi', 'fault',
                                                'severity', 'description'])
        }

    def collect_metrics(self, server, handle):
        g = self.get_metrics()['faults']

        sys = handle.query_dn("sys")
        chassis = self.query(handle.query_children, sys, class_id="EquipmentChassis")
        
        logger.info("{0}: Received {1} chassis from query".format(server, len(chassis)))
        for chassi in chassis:
            faults = self.query(handle.query_children, chassi, class_id="FaultInst")
            if faults:
                logger.info("{0}: {1} Faults detected: {2}".format(server, chassi.dn, faults))
                for fault in faults:
                    g.add_metric(labels=[server, fault.cause, chassi.dn, fault.severity, fault.descr], value=1)
            else:
                logger.info("{0}: {1} No Faults detected.".format(server, chassi.dn))
                g.add_metric(labels=[server, chassi.dn], value=0)
        yield g
