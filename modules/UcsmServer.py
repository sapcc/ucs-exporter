import re
import logging
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsexception import UcsException
import master_password as master_pass
from ucsmsdk.mometa.aaa.AaaUser import AaaUser
import re


logger = logging.getLogger("UcsmServer")


class UcsmServer(object):
    def __init__(self, ucs_server, user, master_password, domain=None):
        self.ucs_server = ucs_server
        self.user = user
        self.master_password = master_password
        self.domain = domain
        self.password = self.get_password()
        self.handle = self._login()

    def get_password(self):
        """
        Get password with decryption
        :return:
        """
        mpw = master_pass.MPW(self.user, self.master_password)
        return UcsmServer.fix_ucsm_password(mpw.password(self.ucs_server))

    def _login(self):
        """
        Login to ucsm server and return handle
        :return:
        """
        if self.domain:
            user = self.domain + "\\" + self.user
        else:
            user = self.user
        handle = UcsHandle(self.ucs_server, user, self.password)

        try:
            handle.login(timeout=5)
        except OSError as e:
            logger.info("Problem logging in to", self.ucs_server, ":", str(e))
            return
        except UcsException as e:
            logger.info("Problem logging in to", self.ucs_server, ":", str(e))
            return

        return handle

    @staticmethod
    def fix_ucsm_password(pwd, repl='@'):
        """Replace forbidden characters with allowed ones"""
        re_pattern = AaaUser.prop_meta['pwd'].restriction.pattern
        unsupported_chars = re.sub( re_pattern, '', pwd )
        if 0 == len(unsupported_chars):
            return pwd
        esc_unsupported_re = '[' + re.escape( unsupported_chars ) + ']'
        safe_pass = re.sub( esc_unsupported_re, repl, pwd )
        # echo("unsupported_chars: %s -> %s"%(unsupported_chars, safe_pass))
        return safe_pass
