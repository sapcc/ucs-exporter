import urllib
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector


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
        return {"license" : GaugeMetricFamily("ucs_server_license", "licenses")}

    def collect_metrics(self):
        print("UcsServerLicenseCollector: Get Updated handles !")
        self.get_handles()

        g = GaugeMetricFamily('ucs_server_license', 'Information about port license',
                              labels=['server', 'port_name'])
        for server, handle in self.handles.items():
            for eth_p in self.query(handle.query_classid, "EtherPIo"):
                port_name = "{}-{}-{}".format(eth_p.switch_id,
                                              eth_p.aggr_port_id,
                                              eth_p.rn)
                license_state = eth_p.lic_state
                labels = [server, port_name]
                g.add_metric(labels=labels, value=self.license_state[license_state])
        yield g
