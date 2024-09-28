class UserRfid:
    def __init__(self, rfid, userid):
        self.__rfid = rfid
        self.__userid = userid

    @property
    def rfid(self):
        return self.__rfid

    @rfid.setter
    def rfid(self, rfid):
        self.__rfid = rfid

    @property
    def userid(self):
        return self.__userid

    @userid.setter
    def userid(self, userid):
        self.__userid = userid

if __name__ == '__main__':
    user_rfid = UserRfid(-1, -1)
    print(user_rfid.userid, user_rfid.rfid)