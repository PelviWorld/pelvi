class Positions:
    def __init__(self, positionsid, positionsnumber, duration, userid):
        self.__positionsid = positionsid
        self.__positionsnumber = positionsnumber
        self.__duration = duration
        self.__userid = userid

    @property
    def positionsid(self):
        return self.__positionsid

    @property
    def positionsnumber(self):
        return self.__positionsnumber

    @positionsnumber.setter
    def positionsnumber(self, positionsnumber):
        self.__positionsnumber = positionsnumber

    @property
    def duration(self):
        return self.__duration

    @duration.setter
    def duration(self, duration):
        self.__duration = duration

    @property
    def userid(self):
        return self.__userid

    @userid.setter
    def userid(self, userid):
        self.__userid = userid

if __name__ == '__main__':
    positions = Positions(-1, 0, -1)
    print(positions.positionsid, positions.positionsnumber, positions.userid)