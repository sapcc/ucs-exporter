import json
from abc import ABC, abstractmethod
from ucsmsdk.ucsexception import UcsException
from modules.UcsmServer import UcsmServer


class BaseCollector(ABC):
    def __init__(self, creds, inventory_file):
        self.creds = creds
        self.inventory_file = inventory_file
        self.handles = {}

    @abstractmethod
    def describe(self):
        pass

    @abstractmethod
    def collect(self):
        pass

    def get_handles(self):
        """
        Return handles to all the servers from inventory.
        :return: dict of handles
                e.g. self.handles = {"server_name": "<server_handle>", ...}
        """
        server_list = self.get_inventory()
        print("Create handles for Ucsm Servers.")
        for server in range(len(server_list)):
            print("Check if handle exists, else login ")
            if self.handles.get(server_list[server]):
                try:
                    if self.handles.get(server_list[server]).login(timeout=5):
                        continue
                except OSError as e:
                    print(e, "May be server not reachable !")
                    self.handles.pop(server_list[server])
            else:
                srv_obj = UcsmServer(server_list[server], self.creds['username'], self.creds['master_password'])
                if srv_obj.handle:
                    self.handles[server_list[server]] = srv_obj.handle
            print(self.handles)

    def logout_handles(self):
        """
        Logout from all the handles
        :return:
        """
        for server, handle in self.handles.items():
            print("Logging out from server {}".format(server))
            handle.logout()

    def get_inventory(self):
        """
        Get updated inventory
        :return:
        """
        with open(self.inventory_file) as json_file:
            data = json.load(json_file)
        return data["servers"]
