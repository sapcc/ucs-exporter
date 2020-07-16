#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    ucs_exporter.py
    Exports prometheus consumable metrics for UCSM/UCSC.
    usage: python3 path/to/ucs_exporter.py -u <user> -p <password> -c <config> -i <inventory>
"""

import time
import json

import optparse
from prometheus_client import CollectorRegistry
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

from modules.main_collector import MainCollector


def get_params():
    """
    Argument parser
    :return: dict of arguments
    """
    parser = optparse.OptionParser()

    parser.add_option("-c", "--config", help="", action="store", dest="conf")
    parser.add_option("-p", "--master-password", help="master password to decrypt mpw", action="store",
                      dest="master_password")
    parser.add_option("-i", "--inventory", help="Server list", action="store", dest="inventory")
    parser.add_option("-u", "--user", help="user used with master password", action="store", dest="user")

    (options, args) = parser.parse_args()
    print(options)
    print(args)
    return options


def get_inventory(params):
    inventory = params.inventory
    with open(inventory) as json_file:
        data = json.load(json_file)
    return data["servers"]


def start_collector(params):
    registry = CollectorRegistry()
    try:
        server_list = get_inventory(params)
        print(server_list, "List of servers")
        creds = {"username": params.user, "password": params.master_password}

        main_collector = MainCollector(servers=server_list, creds=creds)
    except Exception as e:
        print("Check for params, may be missing : {}".format(params))
        print(e)
        return
    try:
        REGISTRY.register(main_collector)
    except Exception as e:
        print("failed to register: {}".format(params))
        print(e)
        return


if __name__ == '__main__':
    params = get_params()
    srv = start_http_server(1234)
    start_collector(params)
    while True:
        time.sleep(3600)
