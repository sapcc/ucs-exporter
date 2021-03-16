import urllib
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.ucsexception import UcsException


class UcsmCRCFaultCollector(BaseCollector):
    def get_metrics(self):
        return {"crc": GaugeMetricFamily("ucsm_crc_error",
                                         "UCSM server CRC errors",
                                         labels=['server', 'port'])
                                         }

    def collect_metrics(self, server, handle):
        g = self.get_metrics()['crc']

        errs = self.query(handle.query_classid, NamingId.ETHER_NI_ERR_STATS)
        for err in errs:
            g.add_metric(labels=[server, err.dn],
                            value=err.crc)
        errs = self.query(handle.query_classid, NamingId.ETHER_ERR_STATS)
        for err in errs:
            g.add_metric(labels=[server, err.dn],
                            value=err.fcs)
        errs = self.query(handle.query_classid, NamingId.ADAPTOR_ETH_PORT_ERR_STATS)
        for err in errs:
            g.add_metric(labels=[server, err.dn],
                            value=err.bad_crc_packets)

        yield g

