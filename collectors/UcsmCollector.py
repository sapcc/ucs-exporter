import urllib
from prometheus_client.core import InfoMetricFamily
from modules.BaseCollector import BaseCollector
from ucsmsdk.ucsexception import UcsException
import logging

logger = logging.getLogger("UcsmCollector")

class UcsmCollector(BaseCollector):
    def get_metrics(self):
        return {"info": InfoMetricFamily('ucsm_info', 'UCSM server information', labels=["server", "firmware_version"])}

    def collect_metrics(self, server, handle):
        logging.info("UcsmCollector: Get updated handles !")
        g = self.get_metrics()['info']

        sys = self.query(handle.query_dn, "sys")
        if not sys:
            return
        firmware_status = list(self.query(handle.query_children, sys, class_id="FirmwareStatus"))
        firmware_version = firmware_status[0].package_version
        # g.add_metric(labels=["server", "firmware_version"], value={"server":server, "firmware_version":firmware_version})
        g.add_metric(labels="firmware", value={"server":server, "firmware_version":firmware_version})

        yield g
