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


if __name__ == '__main__':
    axis1 = Axis(1, "x", 0, 1000, 0)
    axis2 = Axis(2, "y", 0, 1000, 0)
    device = Device(0, "Back", [axis1, axis2])
    print(device.deviceid, device.devicename )
    for axis in device.axislist:
        print(axis.axisname, axis.minvalue, axis.maxvalue, axis.refvalue)
