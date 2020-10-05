from prometheus_client.core import InfoMetricFamily
from modules.BaseCollector import BaseCollector


class UcsmCollector(BaseCollector):
    def describe(self):
        yield InfoMetricFamily("ucsm_metrics", "ucsm_collector_registered")

    def collect(self):
        print("UcsmCollector: Get updated handles !")
        self.get_handles()
        g = InfoMetricFamily('ucsm_info', 'UCSM server information', labels=["server", "firmware_version"])
        for server, handle in self.handles.items():
            sys = handle.query_dn("sys")
            firmware_status = handle.query_children(sys, class_id="FirmwareStatus")
            firmware_version = firmware_status[0].package_version
            # g.add_metric(labels=["server", "firmware_version"], value={"server":server, "firmware_version":firmware_version})
            g.add_metric(labels="firmware", value={"server":server, "firmware_version":firmware_version})
        yield g

