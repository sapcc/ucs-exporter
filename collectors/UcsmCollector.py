#!/usr/bin/python3
# -*- coding: utf-8 -*-

import traceback
import json
from prometheus_client.core import GaugeMetricFamily
from modules.ucsm import UcsmServer
from collectors.ServerLicenseCollector import UcsServerLicenseCollector
from BaseCollector import BaseCollector
from ucsmsdk.ucsexception import UcsException


class UcsmCollector(BaseCollector):
    def __init__(self, creds, inventory_file):
        self.creds = creds
        self.inventory_file = inventory_file
        self.handles = dict()

    def describe(self):
        yield GaugeMetricFamily("ucsm_metrics", "ucsm_collector_registered")

    def get_inventory(self):
        """
        Get updated inventory each time collection happens
        :return:
        """
        with open(self.inventory_file) as json_file:
            data = json.load(json_file)
        return data["servers"]

    def collect(self):
        print("Get updated inventory !")
        server_list = self.get_inventory()

        g = GaugeMetricFamily('ucsm_exporter_info', 'information metric, internal exporter info')

        print("Create handles for Ucsm Servers.")
        for x in range(len(server_list)):
            try:
                print("Check if handle exists, else login ")
                if self.handles.get(server_list[x]):
                    if self.handles.get(server_list[x]).login(timeout=5):
                        continue
                    print("Server not reachable !")
                    return
                else:
                    srv_obj = UcsmServer(server_list[x], self.creds['username'], self.creds['master_password'])
                    self.handles[server_list[x]] = srv_obj.handle
                print(self.handles)
            except OSError as e:
                print(e, "May be server not reachable !")
                return
            except UcsException as e:
                print(e, ", May be check for username and password !")
                return
        g.add_metric(labels=["ucs_get_handles"], value=1)
        yield g

        ucs_license_collector = UcsServerLicenseCollector(self.handles)
        for metric in ucs_license_collector.collect():
            yield metric
