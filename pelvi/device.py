from pelvi.axis import Axis

class Device:
    def __init__(self, deviceid, devicename, axis_list):
        self.__deviceid = deviceid
        self.__devicename = devicename
        self.__axis_list = axis_list

    @property
    def deviceid(self):
        return self.__deviceid

    @property
    def devicename(self):
        return self.__devicename

    @property
    def axislist(self):
        return self.__axis_list
