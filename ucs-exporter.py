#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    ucs_exporter.py
    Exports prometheus consumable metrics for UCSM/UCSC.
    usage: python3 path/to/ucs_exporter.py -u <user> -p <password> -c <config> -i <inventory>
"""

import time
import optparse

from importlib import import_module
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

COLLECTORS = [
    "UcsmCollector",
    "UcsServerLicenseCollector"
]


def get_params():
    """
    Argument parser
    :return: dict of arguments
    """
    parser = optparse.OptionParser()
    required = ["user", "master_password", "inventory"]

    parser.add_option("-c", "--config", help="", action="store", dest="config")
    parser.add_option("-p", "--master-password", help="master password to decrypt mpw", action="store",
                      dest="master_password")
    parser.add_option("-i", "--inventory", help="Server list", action="store", dest="inventory")
    parser.add_option("-u", "--user", help="user used with master password", action="store", dest="user")

    (options, args) = parser.parse_args()
    options = vars(options)
    for option in options:
        if not options[option] and option in required:
            parser.print_help()
            parser.error("Argument {} can't be None ! \n".format(option))
    print(options)
    return options


def register_collectors(params):
    """
    Start collector by registering
    :param params: arguments
    :return:
    """
    creds = {"username": params['user'], "master_password": params['master_password']}
    inventory_file = params["inventory"]

    # Register collectors
    for collector in COLLECTORS:
        REGISTRY.register(getattr(import_module("collectors.{}".format(
                                collector)), collector)(creds, inventory_file))


if __name__ == '__main__':
    params = get_params()
    register_collectors(params)
    start_http_server(9876)
    while True:
        time.sleep(10)
