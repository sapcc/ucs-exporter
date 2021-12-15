from prometheus_client.core import GaugeMetricFamily
from modules.BaseCollector import BaseCollector
import logging
logger = logging.getLogger("UcsPortCollector")

OP_STATE = {
    "up": 1,
    "down": 0
}

SPEED = {
    "10gbps": 10000000000,
    "5gbps":   5000000000,
    "1gbps":   1000000000,
    "100mbps":  100000000,
    "10mbps":    10000000,
    "unknown":         -1
}

ADMIN_STATE = {
    'enabled' : 1,
    'disabled': 0,
    'unknown': -1
}

class UcsPortCollector(BaseCollector):
    def get_metrics(self):
        oper_state = GaugeMetricFamily('ucs_port_op_state', 'State if port is up/down',
                              labels=['server', 'port'])
        oper_speed = GaugeMetricFamily('ucs_port_speed', 'Speed of interface',
                              labels=['server', 'port'])
        admin_state = GaugeMetricFamily('ucs_port_admin_state', 'State of port',
                              labels=['server', 'port'])
        return {"oper_state": oper_state,
                "oper_speed": oper_speed,
                "admin_state": admin_state}

    def collect_metrics(self, server, handle):
        logger.debug("UcsPortCollector.collect()")
        globals().update(self.get_metrics())

        for eth_p in self.query(handle.query_classid, "EtherPIo"):
            labels = [server, eth_p.dn]
            oper_state.add_metric(labels=labels, value=OP_STATE.get(eth_p.oper_state, OP_STATE['down']))
            oper_speed.add_metric(labels=labels, value=SPEED.get(eth_p.oper_speed, SPEED['unknown']))
            admin_state.add_metric(labels=labels, value=ADMIN_STATE.get(eth_p.admin_state, ADMIN_STATE['unknown']))

        yield oper_state
        yield oper_speed
        yield admin_state
