import pynetbox


class Netbox:
    def __init__(self, nb_config):
        self.nb_config = nb_config
        self.nb = self._login()

    def _login(self):
        """
        Login to netbox
        :return:
        """
        nb = pynetbox.api(url=self.nb_config["netbox_url"], token=self.nb_config["netbox_token"])
        return nb

    def get_all_av_zones_from_region(self, region):
        """
        Get all availability zones from region.
        :param region: region name
        :return: List of availability zones
        """
        av_zones = self.nb.dcim.sites.filter(region=region)
        return av_zones

    def get_all_bb_from_av_zones(self, av_zones):
        """
        Get all building blocks from availability zones.
        :param av_zone:
        :return: list of bb's from availability zone
        """
        bbs = {}
        for av_zone in av_zones:
            ucs_servers = self.nb.dcim.devices.filter(q=self.nb_config["query"], tenant=self.nb_config["tenant"],
                                                      status=self.nb_config["status"], site=av_zone)
            bbs.setdefault(av_zone, []).extend([ucs.name.split("-")[1].lower() for ucs in ucs_servers])
        return bbs

    def get_all_bb_from_regions(self, regions):
        """
        Get all building blocks from regions
        :param regions: list of regions
        :return: list of building blocks
        """
        bbs = {}
        for region in regions:
            ucs_servers = self.nb.dcim.devices.filter(q=self.nb_config["query"], tenant=self.nb_config["tenant"],
                                                      status=self.nb_config["status"], region=region)
            bbs.setdefault(region, []).extend([ucs.name.split("-")[1].lower() for ucs in ucs_servers])
        return bbs

    def get_ucsm_servers_from_regions(self, regions):
        """
        Generate UCSM server name from
        :param regions: list of regions
        :return: list of ucsm servers
        """
        ucsm_servers = []
        bbs = self.get_all_bb_from_regions(regions)
        print(bbs)
        for region, bbs in bbs.items():
            for bb in bbs:
                ucsm_servers.append("{}{}{}{}{}".format(self.nb_config["hostname"], bb,
                                                        self.nb_config['azone'], region,
                                                        self.nb_config['domainname']))
        return ucsm_servers
