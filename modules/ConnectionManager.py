import yaml
import logging
import threading
import time
import math
from ucsmsdk.ucsexception import UcsException
from modules.UcsmServer import UcsmServer


logger = logging.getLogger("ConnectionManager")


class DataPoller(threading.Thread):
    """The DataPoller collects the data from one remote host"""
    def __init__(self, manager, config, host):
        threading.Thread.__init__(self)
        self.setName("DataPoller")
        self.manager = manager
        self.setDaemon(True)
        self.config = config
        self.host = host

    def run(self):
        logger.info(f"Start collecting metrics from { self.host }, interval: { self.config['interval'] }")
        while True:
            logger.info(f"Poll server { self.host }")
            try:
                start = time.time()
                for collector in self.manager.get_collectors():
                    try:
                        logger.debug(f"Collect { self.host } : { collector }")
                        collector.update_cache(self.host)
                    except Exception as e:
                        logger.exception(f"Exception in Collector: { e }")
                wait = max(0,  self.config["interval"] - (time.time() - start))
                if wait > 0:
                    time.sleep(wait)
            except Exception as e:
                logger.exception(f"Exception in Poller Thread: { e }")


class ConnectionManager(object):
    def __init__(self, creds, config):
        self.creds = creds
        self.handles = {}
        self.config = config
        self._collectors = []
        self._poll_threads = {}
        # temporary blacklist of unreachable servers
        self.blacklist = {}

    def get_inventory(self):
        """
        Get updated inventory
        :return: list of servers
        """
        config = self.get_config_data()
        server_list = []
        if 'netbox' in config and len(config['netbox']):
            from modules.Netbox import Netbox
            try:
                netbox_data = config['netbox']
                netbox_obj = Netbox(nb_config=netbox_data)
                server_list += netbox_obj.get_ucsm_servers_from_regions(netbox_data["regions"])
            except:
                logger.error("Problem getting server list from netbox")
        if 'servers' in config and type(config['servers']) == list:
            server_list += config['servers']
        logger.debug(f"Serverlist: { server_list }")
        return server_list

    def get_handle(self, host):
        """
        Returns the handle for host
        """
        return self.handles.get(host, None)

    def get_handles(self):
        return self.handles

    def update_handle(self, server):
        """
        Checks if the handle is correct for host. Returns true on success.
        """
        rv = False
        # check if server is currently unreachable
        if server in self.blacklist:
            if self.blacklist[server] <= time.time():
                del self.blacklist[server]
            else:
                return False

        if server in self.handles:
            try:
                self.handles[server].query_dn("sys")
                logger.debug(f"test query to { server } successful")
                rv = True
            except UcsException as e:
                if e.error_code == 552:
                    logger.debug(f"Refresh login to { server }")
                else:
                    logger.error(f"Problem refreshing { server }:{ e }",
                                 extra={'server': server, 'error': e})
                try:
                    rv = False
                except: pass

        if server not in self.handles:
            logger.debug(f"Login into { server }")
            srv_obj = UcsmServer(server, self.creds['username'], self.creds['master_password'], self.config['domain'])
            if not srv_obj.handle:
                if self.config['retry_timeout'] > 0:
                    self.blacklist[server] = time.time() + self.config['retry_timeout']
                    logger.error(f"Problem creating login to { server }. Retry in { self.config['retry_timeout'] } seconds",
                                 extra={'server': server})
                else:
                    logger.error(f"Problem creating login to { server }", extra={'server': server})
                return rv # rv should be False here

            handle = srv_obj.handle
            try:
                if handle.login(timeout=5, auto_refresh=True):
                    self.handles[server] = handle
                    rv = True
            except Exception as e:
                logger.error(f"Problem logging in to { server }: { e }", extra={'server': server, 'error': e})
                rv = False
        return rv

    def update_state(self):
        """
        Return handles to all the servers from inventory.
        :return: dict of handles
                e.g. self.handles = {"server_name": "<server_handle>", ...}
        """
        server_list = self.get_inventory()
        logger.debug(f"Create handles for Ucsm Servers: { server_list }")
        # we iterate over the range to be able to modify the list in the loop body
        rm_connections = set(self.handles.keys())
        for sid in range(len(server_list)):
            server = server_list[sid]
            active = self.update_handle(server)
            if not active:
                continue
            if server in rm_connections:
                rm_connections.remove(server)
            self.start_poll_thread(server)
            # refresh otherwise the handle gets stale

        # remove old connections no longer in server list
        for s in rm_connections:
            logger.info(f"remove old server connection: { s }")
            try:
                del self.handles[s]
            except: pass

        return self.handles


    def logout_handles(self):
        """
        Logout from all the handles
        :return:
        """
        rm = []
        for server, handle in self.handles.items():
            logger.info(f"Logging out from server { server }")
            handle.logout()
            rm.append(server)
        for s in rm:
            del self.handles[s]

    def get_config_data(self, key=None):
        """

        :return:
        """
        try:
            with open(self.config['config']) as conf:
                content = yaml.safe_load(conf)
        except FileNotFoundError as e:
            logger.error("Config File not found (%s): %s", self.config['config'], str(e))
            exit(1)

        if key:
            return content[key]
        else:
            return content

    def register_collector(self, collector):
        if collector not in self._collectors:
            self._collectors.append(collector)
        else:
            logger.error(f"Collector { collector } is already registered")

    def get_collectors(self):
        return self._collectors

    def start_poll_thread(self, host):
        current = self._poll_threads.get(host, None)
        if current:
            if not current.is_alive():
                # thread is dead, create a new one
                self._poll_threads.pop(host)
            else:
                return current
        current = self._poll_threads[host] = DataPoller(self, self.config, host)
        current.start()

    def run_check_loop(self):
        while True:
            logger.debug("check server threads")
            self.update_state()
            logger.debug(f"sleeping for scrape interval { self.config['scrape_interval'] }")
            time.sleep(self.config['scrape_interval'])
