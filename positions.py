class Positions:
    def __init__(self, positionsid, positionsnumber, userid):
        self.__positionsid = positionsid
        self.__positionsnumber = positionsnumber
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
    def userid(self):
        return self.__userid

if __name__ == '__main__':
    positions = Positions(-1, 0, -1)
    print(positions.positionsid, positions.positionsnumber, positions.userid)