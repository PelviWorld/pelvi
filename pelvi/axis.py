class Axis:
    def __init__(self, axisid, axisname, minvalue, maxvalue, refvalue):
        self.__axisid = axisid
        self.__axisname = axisname
        self.__minvalue = minvalue
        self.__maxvalue = maxvalue
        self.__refvalue = refvalue

    @property
    def axisid(self):
        return self.__axisid

    @property
    def axisname(self):
        return self.__axisname

    @property
    def minvalue(self):
        return self.__minvalue

    @property
    def maxvalue(self):
        return self.__maxvalue

    @property
    def refvalue(self):
        return self.__refvalue

if __name__ == '__main__':
    axis = Axis(1, "x", 0, 1000, 0)
    print(axis.axisid, axis.axisname, axis.minvalue, axis.maxvalue, axis.refvalue)