from prometheus_client.core import GaugeMetricFamily
from ucsmsdk.ucsconstants import NamingId
from modules.BaseCollector import BaseCollector


class UcsmDIMMErrorsCollector(BaseCollector):
    def get_metrics(self):
        return {
            "correctable": GaugeMetricFamily("correctable_errors",
                                        "UCSM server correctable DIMM errors",
                                        labels=['server', 'mem_unit']),
            "uncorrectable": GaugeMetricFamily("uncorrectable_errors",
                                        "UCSM server uncorrectable DIMM errors",
                                        labels=['server', 'mem_unit'])

        }

    def collect_metrics(self, server, handle):
        correctable = self.get_metrics()['correctable']
        uncorrectable = self.get_metrics()['uncorrectable']

        mem_err_stat = self.query(handle.query_classid, NamingId.MEMORY_ERROR_STATS)
        for mem_stat in mem_err_stat:
            correctable_errors = mem_stat.dram_write_data_correctable_crc_errors
            correctable.add_metric(labels=[server, mem_stat.dn],
                                   value=correctable_errors)
            uncorrectable_errors = mem_stat.dram_write_data_un_correctable_crc_errors
            uncorrectable.add_metric(labels=[server, mem_stat.dn],
                                   value=uncorrectable_errors)
        yield correctable
        yield uncorrectable
