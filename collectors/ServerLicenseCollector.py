from prometheus_client.core import GaugeMetricFamily


class UcsServerLicenseCollector():
    def __init__(self, handles):
        self.handles = handles
        self.license_state = {
            "license-expired": 0,
            "not-applicable": 1
        }

    def describe(self):
        yield GaugeMetricFamily("ucs_server_license", "licenses")

    def collect(self):
        print("Get license info of ports ")
        g = GaugeMetricFamily('ucs_license', 'Information about port license')
        for server, handle in self.handles.items():
            # Currently kept this as static, going to change
            dn = "sys/switch-{}/slot-{}/switch-ether/port-{}".format("A", 1, 27)
            mo = handle.query_dn(dn)

            license_state = mo.lic_state
            labels = [server, "27"]
            g.add_metric(labels=labels, value=self.license_state[license_state])
        yield g
