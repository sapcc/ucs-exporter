from prometheus_client.core import GaugeMetricFamily
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

        memArray = self.query(handle.query_classid, "MemoryArray")
        for mem_arr in memArray:
            for mem_unit in handle.query_children(mem_arr,
                                                 class_id="MemoryUnit"):
                for mem_stat in handle.query_children(mem_unit, class_id="MemoryErrorStats"):
                    correctable_errors = mem_stat.dram_write_data_correctable_crc_errors
                    correctable.add_metric(labels=[server, mem_unit.dn],
                                           value=correctable_errors)
                    uncorrectable_errors = mem_stat.dram_write_data_un_correctable_crc_errors
                    uncorrectable.add_metric(labels=[server, mem_unit.dn],
                                           value=uncorrectable_errors)
        yield correctable
        yield uncorrectable
