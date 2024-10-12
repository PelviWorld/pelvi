class Position:
    def __init__(self, positionid, positionsid, deviceaxisid, position = 0):
        self.__positionid = positionid
        self.__positionsid = positionsid
        self.__deviceaxisid = deviceaxisid
        self.__position = position

    @property
    def positionid(self):
        return self.__positionid

    @positionid.setter
    def positionid(self, positionid):
        self.__positionid = positionid

    @property
    def positionsid(self):
        return self.__positionsid

    @positionsid.setter
    def positionsid(self, positionsid):
        self.__positionsid = positionsid

    @property
    def deviceaxisid(self):
        return self.__deviceaxisid

    @deviceaxisid.setter
    def deviceaxisid(self, deviceaxisid):
        self.__deviceaxisid = deviceaxisid

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position = position


if __name__ == '__main__':
    pos = Position(0, 0, 1)
    print(pos.positionid, pos.positionsid, pos.deviceaxisid)