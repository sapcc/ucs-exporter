#!/usr/bin/python3
# -*- coding: utf-8 -*-

import traceback

from prometheus_client import Metric, REGISTRY, start_http_server
from modules.ucsm import UcsmServer
from modules.server_license import UcsServerLicense

class MainCollector(object):
    def __init__(self, servers, creds):
        self.servers = servers
        self.creds = creds
        self.handles = dict()

    def __del__(self):
        print("logging out of handles")
        # for x in range(self.handles):
        #     if len(self.handles)>x:
        #         self.handles[x].logout()

    def collect(self):
        print("Create handles for UcsmServers. ")
        info_metric = Metric('ucs_exporter_info', 'information metric, internal exporter info', "gauge")


        for x in range(len(self.servers)):
            try:
                print("Check if handle exists, else login ")
                if self.handles.get(self.servers[x]):
                    continue
                else:
                    srv_obj = UcsmServer(self.servers[x], self.creds['username'], self.creds['password'])
                    self.handles[self.servers[x]] = srv_obj.handle
                print(self.handles)
            except Exception as e:
                print(e, "This in exception")
                print(traceback.format_exc())

                for handle in self.handles:
                    del handle
                return
        info_metric.add_sample('ucs_exporter_info', labels={
                    "component": "ucs_credentials",
                    "desc": "ucs",
                    "stacktrace": "collector"
                    }, value=1)
        yield info_metric

        ucs_license_collector = UcsServerLicense(self.handles)
        for metric in ucs_license_collector.collect():
            yield metric
