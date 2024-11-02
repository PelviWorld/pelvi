from pelvi.axis import Axis

class Blockedvalues:
    def __init__(self, axis, minvalue, maxvalue, blockedvalueid=-1):
        self.__axis = axis
        self.__minvalue = minvalue
        self.__maxvalue = maxvalue
        self.__blockedvalueid = blockedvalueid

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

    @property
    def blockedvalueid(self):
        return self.__blockedvalueid

    @blockedvalueid.setter
    def blockedvalueid(self, blockedvalueid):
        self.__blockedvalueid = blockedvalueid


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
