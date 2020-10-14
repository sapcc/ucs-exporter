import yaml
from abc import ABC, abstractmethod
from modules.UcsmServer import UcsmServer
from ucsmsdk.ucsexception import UcsException
from modules.Netbox import Netbox


class BaseCollector(ABC):
    def __init__(self, creds, config):
        self.creds = creds
        self.handles = {}
        self.config = config

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
        print("Create handles for Ucsm Servers.", server_list)
        for server in range(len(server_list)):
            print("Check if handle exists, else login ")
            if self.handles.get(server_list[server]):
                try:
                    if self.handles.get(server_list[server]).login(timeout=5):
                        continue
                except OSError as e:
                    print("Problem logging in to", server_list[server], ":", str(e))
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
            try:
                handle.logout()
            except OSError as e:
                print("Problem logging out ", server, ":", str(e))
                return
            except UcsException as e:
                print("Problem logging out ", server, ":", str(e))
                return

    def get_config_data(self, keys=None):
        """

        :return:
        """
        content_dict = {}
        with open(self.config) as conf:
            content = yaml.safe_load(conf)
        if keys:
            for key in keys:
                content_dict.update(content[key])
            return content_dict
        else:
            return content

    def get_inventory(self):
        """
        Get updated inventory
        :return: list of servers
        """
        netbox_data = self.get_config_data(keys=["netbox"])
        netbox_obj = Netbox(nb_config=netbox_data)
        server_list = netbox_obj.get_ucsm_servers_from_regions(netbox_data["regions"])
        return server_list
