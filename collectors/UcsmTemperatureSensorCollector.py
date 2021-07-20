import logging
from ucsmsdk.ucsconstants import NamingId
from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
import math

logger = logging.getLogger("UcsmTemperatureSensorCollector")

class UcsmTemperatureSensorCollector(BaseCollector):
    def get_metrics(self):
        return {
            "sensor": GaugeMetricFamily("ucsm_temperature_sensor",
                                        "UCSM temperature sensor for motherboard/cpu/psu",
                                        labels=['server', 'component',
                                                'description'])
        }

    def collect_metrics(self, server, handle):
        logger.debug("Collecting Metrics ")
        g = self.get_metrics()['sensor']

        mb_temp = handle.query_classid(NamingId.COMPUTE_MB_TEMP_STATS)
        for temp in mb_temp:
            value_rear = math.nan if temp.fm_temp_sen_rear == 'not-applicable' else temp.fm_temp_sen_rear
            g.add_metric(labels=[server, temp.dn, "motherboard_rear_temperature"],
                                    value=value_rear)
            value_io = math.nan if temp.fm_temp_sen_io == 'not-applicable' else temp.fm_temp_sen_io
            g.add_metric(labels=[server, temp.dn, "motherboard_front_temperature"],
                                    value=value_io)

        cpu_temp = handle.query_classid(NamingId.PROCESSOR_ENV_STATS)
        for temp in cpu_temp:
            g.add_metric(labels=[server, temp.dn, "cpu_temperature"],
                                    value=temp.temperature)

        psu_temp = handle.query_classid(NamingId.EQUIPMENT_PSU_STATS)
        for temp in psu_temp:
            g.add_metric(labels=[server, temp.dn, "psu_temperature"],
                                    value=temp.ambient_temp)
        yield g
