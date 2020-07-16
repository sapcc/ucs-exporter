from prometheus_client import Metric


class UcsServerLicense:
    def __init__(self, handles):
        self.handles = handles

    def collect(self):
        print("Get license info of ports ")
        license_state_metric = Metric('ucs_license', 'Information about port license', "gauge")
        for server, handle in self.handles.items():
            dn = "sys/switch-{}/slot-{}/switch-ether/port-{}".format("A", 1, 8)
            mo = handle.query_dn(dn)

            license_state = mo.lic_state
            labels = {"server" : server,
                      "port": "8",
                      "license-state": license_state}
            license_state_metric.add_sample("ucsm_port_license", labels=labels, value=0)
        yield license_state_metric
