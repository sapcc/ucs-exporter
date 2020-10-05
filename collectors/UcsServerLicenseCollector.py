import urllib
from prometheus_client.core import GaugeMetricFamily
from BaseCollector import BaseCollector
from ucsmsdk.ucsexception import UcsException

class UcsServerLicenseCollector(BaseCollector):
    def __init__(self, creds, config):
        super().__init__(creds, config)
        self.license_state = {
            "license-expired": 0,
            "license-graceperiod": 1,
            "not-applicable": 2,
            "license-ok": 3
        }

    def describe(self):
        yield GaugeMetricFamily("ucs_server_license", "licenses")

    def collect(self):
        print("UcsServerLicenseCollector: Get Updated handles !")
        self.get_handles()

        g = GaugeMetricFamily('ucs_server_license', 'Information about port license',
                              labels=['server', 'port_name'])
        for server, handle in self.handles.items():
            try:
                for eth_p in handle.query_classid("EtherPIo"):
                    port_name = "{}-{}-{}".format(eth_p.switch_id,
                                                  eth_p.aggr_port_id,
                                                  eth_p.rn)
                    license_state = eth_p.lic_state
                    labels = [server, port_name]
                    g.add_metric(labels=labels, value=self.license_state[license_state])
            except urllib.error.URLError as e:
                print("URLError: ", e.reason)
            except UcsException as e:
                print("UcsException : ", str(e))
        yield g

        self.logout_handles()
