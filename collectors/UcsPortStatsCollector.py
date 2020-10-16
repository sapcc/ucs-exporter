from prometheus_client.core import CounterMetricFamily
from ucsmsdk.ucsconstants import NamingId
from modules.BaseCollector import GenericClassCollector
import logging
logger = logging.getLogger("UcsPortErrStatsCollector")


class UcsPortErrStatsCollector(GenericClassCollector):
    KEYS = ['align', 'deferred_tx', 'fcs', 'int_mac_rx', 'int_mac_tx', 'out_discard', 'rcv', 'under_size', 'xmit', 'bad_crc_packets']
    LABELS = labels=['server', 'port_name']
    PREFIX = 'ucs_port_err_{key}'
    DESCRIPTION = "Ethernet error counter for statistic: {key}"
    CLASS = NamingId.ETHER_ERR_STATS

class UcsPortRXStatsCollector(GenericClassCollector):
    KEYS = ['broadcast_packets', 'jumbo_packets', 'multicast_packets', 'total_bytes', 'total_packets', 'unicast_packets']
    LABELS = ['server', 'port_name']
    PREFIX = 'ucs_port_rx_{key}'
    DESCRIPTION = "Ethernet RX counter: {key}"
    CLASS = NamingId.ETHER_RX_STATS

class UcsPortTXStatsCollector(UcsPortRXStatsCollector):
    PREFIX = 'ucs_port_tx_{key}'
    DESCRIPTION = "Ethernet TX counter: {key}"
    CLASS = NamingId.ETHER_TX_STATS
