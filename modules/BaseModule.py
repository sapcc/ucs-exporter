import re

import master_password as master_pass
from ucsmsdk.mometa.aaa.AaaUser import AaaUser

def fix_ucsm_password( pwd, repl='@' ):
    re_pattern = AaaUser.prop_meta['pwd'].restriction.pattern
    unsupported_chars = re.sub( re_pattern, '', pwd )
    if 0 == len(unsupported_chars):
        return pwd
    esc_unsupported_re = '[' + re.escape( unsupported_chars ) + ']'
    safe_pass = re.sub( esc_unsupported_re, repl, pwd )
    # echo("unsupported_chars: %s -> %s"%(unsupported_chars, safe_pass))
    return safe_pass

class BaseClass(object):
    def __init__(self, server, user, master_pasword):
        self.ucs_server = server
        self.user = user
        self.master_password = master_pasword

    def get_password(self):
        """
        Get password with decryption
        :return:
        """
        mpw = master_pass.MPW(self.user, self.master_password)
        return fix_ucsm_password(mpw.password(self.ucs_server))
