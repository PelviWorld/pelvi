from axis import Axis

class Blockedvalues:
    def __init__(self, axis, minvalue, maxvalue):
        self.__axis = axis
        self.__minvalue = minvalue
        self.__maxvalue = maxvalue

    @property
    def axis(self):
        return self.__axis

    @property
    def minvalue(self):
        return self.__minvalue

    @minvalue.setter
    def minvalue(self, minvalue):
        self.__minvalue = minvalue

    @property
    def maxvalue(self):
        return self.__maxvalue

    @maxvalue.setter
    def maxvalue(self, maxvalue):
        self.__maxvalue = maxvalue


class Blockedarea:
    def __init__(self, userid, blockedvalues):
        self.__userid = userid
        self.__blockedvalues = blockedvalues

    @property
    def userid(self):
        return self.__userid

    @property
    def blockedvalues(self):
        return self.__blockedvalues

if __name__ == '__main__':
    axis1 = Axis(1, "x", 0, 1000, 0)
    axis2 = Axis(2, "y", 0, 1000, 0)
    blocked1 = Blockedvalues(axis1, 300, 1000)
    blocked2 = Blockedvalues(axis2, 300, 500)
    blockedarea = Blockedarea(1, [blocked1, blocked2])
    for blocked in blockedarea.blockedvalues:
        print(blocked.axis.axisname, blocked.minvalue, blocked.maxvalue)
