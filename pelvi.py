from pelvidata import Pelvidata

class Pelvi:
    def __init__(self):
        self.__pelvidata = Pelvidata()
        self.__user = self.__pelvidata.get_default_user()
        self.__load_user_data(self.__user.userid)
        self.__device_list = self.__pelvidata.get_device_list()

    def __load_user_data(self, userid):
        self.__position_list = self.__pelvidata.get_position_list(userid)
        self.__blocked_list = self.__pelvidata.get_blocked_list(userid)
        self.__device_axis_list = self.__pelvidata.get_device_axis_list()

    @property
    def user(self):
        return self.__user

    @property
    def device_list(self):
        return self.__device_list

    @property
    def position_list(self):
        return self.__position_list

    @property
    def blocked_list(self):
        return self.__blocked_list

    def axis_name_for_device_axisid(self, device_axis_id):
        return self.__device_axis_list[device_axis_id]


if __name__ == '__main__':
    pelvi = Pelvi()
    print("USER:", pelvi.user.name, pelvi.user.lastname)
    print("DEVICES:")
    for device in pelvi.device_list:
        print(device.devicename)
        print("DEVICEAXISES:")
        for axis in device.axislist:
            print(axis.axisname, axis.minvalue, axis.maxvalue, axis.refvalue)
    print("POSITIONS:")
    for positions in pelvi.position_list:
        print("Positionid:", positions[0].positionsid, "number:", positions[0].positionsnumber)
        for power in positions[1]:
            print("Device", power['deviceid'], power['power'])
        for axis_position in positions[2]:
            print("Axis", pelvi.axis_name_for_device_axisid(axis_position.deviceaxisid), "Position", axis_position.position)

    print("BLOCKS:")
    for blocked in pelvi.blocked_list:
        print("Blockvalue Axis:", blocked.axis, "Min Value:", blocked.minvalue, "Max Value", blocked.maxvalue)
