#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    ucs_exporter.py
    Exports prometheus consumable metrics for UCSM/UCSC.
    usage: python3 path/to/ucs_exporter.py -u <user> -p <password> -c <config.yaml>
 """

import time
import optparse
import logging
import sys

from importlib import import_module
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from modules.ConnectionManager import ConnectionManager

COLLECTORS = [
    "UcsmCollector",
    "UcsServerLicenseCollector",
    "UcsmChassisFaultCollector",
    "UcsPortCollector",
    "UcsPortStatsCollector.UcsPortErrStatsCollector",
    "UcsPortStatsCollector.UcsPortRXStatsCollector",
    "UcsPortStatsCollector.UcsPortTXStatsCollector",
    "UcsmCRCFaultCollector",
    "UcsmDIMMErrorsCollector",
    "UcsmScalabilityPortStatus",
    "UcsmTemperatureSensorCollector"
]

logger = logging.getLogger("ucs-exporter")

def get_params():
    """
    Argument parser
    :return: dict of arguments
    """
    parser = optparse.OptionParser()
    required = ["user", "master_password", "config"]

    parser.add_option("-c", "--config", help="", action="store", dest="config")
    parser.add_option("-p", "--master-password", help="master password to decrypt mpw", action="store",
                      dest="master_password")
    parser.add_option("-d", "--domain", help="domain used for login", action="store", dest="domain")
    parser.add_option("-u", "--user", help="user used with master password", action="store", dest="user")
    parser.add_option("-v", "--verbose", help="increase verbosity", dest="verbose", action='count', default=0)
    parser.add_option("-i", "--interval", dest="interval", type=int, help="poll data in seconds", default=300)
    parser.add_option("-s", "--scrape_interval", dest="scrape_interval", type=int,
                      help="scrape data interval for internal cache", default=300)
    parser.add_option("-r", "--retry-timeout", dest="retry_timeout", type=int, help="Retry unreachable servers after N seconds", default=60)
    parser.add_option("--port", help="Port to listen on", dest="port", type=int, default=9876)

    (options, args) = parser.parse_args()
    options = vars(options)
    for option in options:
        if not options[option] and option in required:
            parser.print_help()
            parser.error("Argument {} can't be None ! \n".format(option))

    format = '%(asctime)-15s %(process)d %(levelname)s %(filename)s:%(lineno)d %(message)s'
    loglevel = logging.INFO
    if options['verbose'] > 0:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, stream=sys.stdout, format=format)

    return options


def register_collectors(params):
    """
    Start collector by registering
    :param params: arguments
    :return: manager instance
    """
    creds = {"username": params['user'], "master_password": params['master_password']}

    manager = ConnectionManager(creds, params)
    # Register collectors
    for collector in COLLECTORS:
        if "." in collector:
            mod, name = collector.split(".", 1)
            instance = getattr(import_module("collectors.{}".format(mod)), name)(manager)

        else:
            instance = getattr(import_module("collectors.{}".format(collector)), collector)(manager)

        logger.debug(f"Register collector: { instance }")
        REGISTRY.register(instance)
        manager.register_collector(instance)

    return manager

if __name__ == '__main__':
    params = get_params()
    logger.debug(f"Params are { params }")
    manager = register_collectors(params)
    logger.info(f"Listening to port: { params['port'] }")
    logger.info(f"Poll interval: { params['interval'] }")
    start_http_server(params['port'])
    try:
        manager.run_check_loop()
    except KeyboardInterrupt:
        logger.info("Stopping UCS-Exporter")
