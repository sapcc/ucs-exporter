import urllib
from prometheus_client.core import InfoMetricFamily
from BaseCollector import BaseCollector
from ucsmsdk.ucsexception import UcsException

class UcsmCollector(BaseCollector):
    def __init__(self, creds, config):
        super().__init__(creds, config)

    def describe(self):
        yield InfoMetricFamily("ucsm_firmware", "ucsm_collector_registered")

    def collect(self):
        print("UcsmCollector: Get updated handles !")
        self.get_handles()
        i = InfoMetricFamily('ucsm_firmware', 'UCSM server information')
        for server, handle in self.handles.items():
            try:
                sys = handle.query_dn("sys")
                firmware_status = handle.query_children(sys, class_id="FirmwareStatus")
                firmware_version = firmware_status[0].package_version
                i.add_metric(labels=["server", "firmware_version"], value={"server":server,
                                                                           "firmware_version":firmware_version})
            except urllib.error.URLError as e:
                print("URLError: ", e.reason)
            except UcsException as e:
                print("UcsException : ", str(e))
        yield i

        self.logout_handles()

