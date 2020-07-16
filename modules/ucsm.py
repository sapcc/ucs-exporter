from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsexception import UcsException
import master_password

class UcsmServer:
    def __init__(self, ucsm_server, user, master_password):
        self.ucsm_server = ucsm_server
        self.user = user
        self.master_password = master_password
        self.password = self._get_password()
        self.handle = self._login()

    def _get_password(self):
        """
        Get password with decryption
        :return:
        """
        mpw = master_password.MPW(self.user, self.master_password)
        return mpw.password(self.ucsm_server)

    def _login(self):
        """
        Login to ucsm server and return handle
        :return:
        """
        print("Inside ucsm server, login", self.user, self.password)
        handle = UcsHandle(self.ucsm_server, self.user, self.password)

        try:
            handle.login()
        except UcsException as e:
            print(e)

        return handle
