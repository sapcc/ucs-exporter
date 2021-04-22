import urllib
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
import logging

logger = logging.getLogger("UcsServerLicenseCollector")

class UcsServerLicenseCollector(BaseCollector):
    def __init__(self, manager):
        super().__init__(manager)
        self.license_state = {
            "license-expired": 0,
            "license-graceperiod": 1,
            "not-applicable": 2,
            "license-ok": 3
        }

    def get_metrics(self):
        return {"license" : GaugeMetricFamily("ucs_server_license", "licenses",
                                              labels=['server', 'port_name'])}

    def collect_metrics(self, server, handle):
        logger.info("UcsServerLicenseCollector: Get Updated handles !")

        g = self.get_metrics()["license"]

        for eth_p in self.query(handle.query_classid, "EtherPIo"):
            license_state = eth_p.lic_state
            labels = [server, eth_p.dn]
            g.add_metric(labels=labels, value=self.license_state[license_state])

        yield g
