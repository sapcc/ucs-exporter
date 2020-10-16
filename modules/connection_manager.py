import json
import logging
from ucsmsdk.ucsexception import UcsException
from modules.UcsmServer import UcsmServer

logger = logging.getLogger("BaseCollector")

class ConnectionManager(object):
    def __init__(self, creds, config):
        self.creds = creds
        self.handles = {}
        self.config = config

    def get_inventory(self):
        """
        Get updated inventory
        :return: list of servers
        """
        config = self.get_config_data()
        server_list = []
        if 'netbox' in config and len(config['netbox']):
            from modules.Netbox import Netbox

            netbox_data = config['netbox']
            netbox_obj = Netbox(nb_config=netbox_data)
            server_list += netbox_obj.get_ucsm_servers_from_regions(netbox_data["regions"])
        if 'servers' in config and type(config['servers']) == list:
            server_list += config['servers']
        logger.debug("Serverlist: %s" %server_list)
        return server_list

    def get_handles(self):
        """
        Return handles to all the servers from inventory.
        :return: dict of handles
                e.g. self.handles = {"server_name": "<server_handle>", ...}
        """
        server_list = self.get_inventory()
        logger.debug("Create handles for Ucsm Servers: %s", server_list)
        #import traceback
        #traceback.print_stack()
        # we iterate over the range to be able to modify the list in the loop body
        rm_connections = set(self.handles.keys())
        for sid in range(len(server_list)):
            server = server_list[sid]
            if server in self.handles:
                try:
                    self.handles[server].query_dn("sys")
                    logger.debug("test query to %s successful" % server)
                    if server in rm_connections:
                        rm_connections.remove(server)
                except UcsException as e:
                    if e.error_code == 552:
                        logger.debug("Refresh login to %s" % server)
                    else:
                        logger.error("Problem refreshing %s:%s", server, str(e), extra={'server': server, 'error': e})
                    del self.handles[server]

            if server not in self.handles:
                logger.debug("Login into %s" % server)
                srv_obj = UcsmServer(server, self.creds['username'], self.creds['master_password'])
                if not srv_obj.handle:
                    logger.error("Problem creating login to %s", server, extra={'server': server})
                    continue
                    
                handle = srv_obj.handle
                try:
                    if handle.login(timeout=5, auto_refresh=True):
                        self.handles[server] = handle
                        if server in rm_connections:
                            rm_connections.remove(server)
                        continue
                except Exception as e:
                    logger.error("Problem logging in to %s:%s", server, str(e), extra={'server': server, 'error': e})
            # refresh otherwise the handle gets stale

            #else:
            #    rm_connections.remove(server)
        # remove old connections no longer in server list
        for s in rm_connections:
            logger.info("remove old server connection: %s", s)
            del self.handles[s]

        return self.handles


    def logout_handles(self):
        """
        Logout from all the handles
        :return:
        """
        rm = []
        for server, handle in self.handles.items():
            logger.info("Logging out from server {}".format(server))
            handle.logout()
            rm.append(server)
        for s in rm:
            del self.handles[s]

    def get_config_data(self, key=None):
        """

        :return:
        """
        with open(self.config) as conf:
            content = json.load(conf)
        if key:
            return content[key]
        else:
            return content
