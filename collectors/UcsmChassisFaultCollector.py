import urllib
import logging
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector


logger = logging.getLogger("UcsmChassisCollector")


class UcsmChassisFaultCollector(BaseCollector):
    def get_metrics(self):
        return {
            "faults": GaugeMetricFamily("ucsm_chassis_faults", "UCSM server chassis faults", labels=['server', 'chassi', 'fault', 'severity', 'description'])
        }

    def collect_metrics(self, server, handle):
        logger.debug("Collecting Metrics ")
        g = self.get_metrics()['faults']

        sys = handle.query_dn("sys")
        chassis = self.query(handle.query_children, sys, class_id="EquipmentChassis")

        logger.info("{0}: Received {1} chassis from query".format(server, len(chassis)))
        for chassi in chassis:
            faults = self.query(handle.query_children, chassi, class_id="FaultInst")
            if faults:
                for fault in faults:
                    logger.info("{0}: {1} Chassis fault detected: {2}".format(server, chassi.dn, fault.severity))
                    g.add_metric(labels=[server, chassi.dn, fault.cause, fault.severity, fault.descr], value=1)
            else:
                logger.info("{0}: {1} No Chassis faults detected.".format(server, chassi.dn))
                g.add_metric(labels=[server, chassi.dn], value=0)
        yield g
