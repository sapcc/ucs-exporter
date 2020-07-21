import master_password as master_pass


class BaseClass:
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
        return mpw.password(self.ucs_server)
