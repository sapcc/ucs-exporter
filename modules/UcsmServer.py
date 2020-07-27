from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsexception import UcsException
from BaseModule import BaseClass


class UcsmServer(BaseClass):
    def __init__(self, ucs_server, user, master_password):
        super().__init__(ucs_server, user, master_password)
        self.password = self.get_password()
        self.handle = self._login()

    def _login(self):
        """
        Login to ucsm server and return handle
        :return:
        """
        print("Logging in first time !")
        handle = UcsHandle(self.ucs_server, self.user, self.password)

        try:
            handle.login(timeout=5)
        except OSError as e:
            print("Problem logging in to", self.ucs_server, ":", str(e))
            return
        except UcsException as e:
            print("Problem logging in to", self.ucs_server, ":", str(e))
            return

        return handle
