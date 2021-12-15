import urllib
import logging
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector


logger = logging.getLogger("UcsmLicenseCollector")


class UcsmPortLicenseCollector(BaseCollector):
    def __init__(self, manager):
        super().__init__(manager)
        self.license_state = {
            "license-expired": 0,
            "license-graceperiod": 1,
            "not-applicable": 2,
            "license-ok": 3
        }

    def get_metrics(self):
        return {"license" : GaugeMetricFamily("ucsm_port_license", "licenses",
                                              labels=['server', 'port', 'type', 'transport', 'license_state'])}

    def collect_metrics(self, server, handle):
        logger.debug("Collecting Metrics ")

        g = self.get_metrics()["license"]

        for eth_p in self.query(handle.query_classid, "EtherPIo"):
            license_state = eth_p.lic_state
            labels = [server, eth_p.dn, eth_p.if_type, eth_p.transport, eth_p.lic_state]
            if license_state == 'not-applicable':
                logger.debug("{0}: Port {1} not applicable.".format(server, eth_p.dn))
                continue

            if license_state == 'license-ok':
                logger.debug("{0}: Port {1} license ok.".format(server, eth_p.dn))
                g.add_metric(labels=labels, value=0)
            else:
                logger.warning("{0}: Port {1} {2}.".format(server, eth_p.dn, eth_p.lic_state.replace("-"," ")))
                g.add_metric(labels=labels, value=1)

        yield g
