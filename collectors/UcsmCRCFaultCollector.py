import urllib
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.ucsexception import UcsException


class UcsmCRCFaultCollector(BaseCollector):
    def get_metrics(self):
        return {"crc": GaugeMetricFamily("ucsm_crc_error", "ucsm_crc_collector")}

    def collect_metrics(self):
        self.get_handles()
        g = GaugeMetricFamily('ucsm_crc_error', 'UCSM server CRC errors',
                              labels=['server', 'port'])
        for server, handle in self.handles.items():
            try:
                errs = handle.query_classid(NamingId.ETHER_NI_ERR_STATS)
                for err in errs:
                    g.add_metric(labels=[server, err.dn],
                                 value=err.crc)
                errs = handle.query_classid(NamingId.ETHER_ERR_STATS)
                for err in errs:
                    g.add_metric(labels=[server, err.dn],
                                 value=err.fcs)
                errs = handle.query_classid(NamingId.ADAPTOR_ETH_PORT_ERR_STATS)
                for err in errs:
                    g.add_metric(labels=[server, err.dn],
                                 value=err.bad_crc_packets)
            except urllib.error.URLError as e:
                print("URLError", server, e.reason)
            except UcsException as e:
                print("UcsException : ", server, str(e))
        yield g

        self.logout_handles()

