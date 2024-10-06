from pelvidata import Pelvidata

class Pelvi:
    def __init__(self):
        self.__pelvidata = Pelvidata()
        self.__user = self.__pelvidata.get_default_user()
        self.__device_list = self.__pelvidata.get_device_list()
        self.__load_user_data(self.__user.userid)

    def __load_user_data(self, userid):
        self.__position_list = self.__pelvidata.get_position_list(userid)
        self.__blocked_list = self.__pelvidata.get_blocked_list(userid)
        self.__device_axis_list = self.__pelvidata.get_device_axis_list()

    def load_user(self, name, lastname):
        return self.__pelvidata.load_user(name, lastname)

    def __find_position(self, axis):
        for positions in self.__position_list:
            for position in positions[2]:
                axisid = position.deviceaxisid
                axisname = self.axis_name_for_device_axisid(axisid)
                if axis == axisname:
                    return position

    def move_axis_by(self, axis, value):
        position = self.__find_position(axis)
        if position:
            position.position = position.position + value

    def move_axis_to(self, axis, value):
        position = self.__find_position(axis)
        if position:
            position.position = value

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

    def add_new_user(self, name, lastname):
        if not self.__pelvidata.check_user_name_not_in_use(name, lastname):
            userid = self.load_user(name, lastname)
            self.__load_user_data(userid)
            return
        self.__user.name = name
        self.__user.lastname = lastname
        self.__user.userid = self.__pelvidata.add_new_user(name, lastname)

        for position in self.__position_list:
            position[0].userid = self.__user.userid
            positionsid = self.__pelvidata.add_new_positions_head(position[0])
            for position_in_positionlist in position[2]:
                position_in_positionlist.positionsid = positionsid
                self.__pelvidata.add_new_position(position_in_positionlist)

        self.__pelvidata.add_new_blocked_area(self.__user.userid, self.__blocked_list)

    def axis_name_for_device_axisid(self, device_axis_id):
        return self.__device_axis_list[device_axis_id]

    def print_user_data(self):
        print("USER:", self.user.name, self.user.lastname)
        print("DEVICES:")
        for device in self.device_list:
            print(device.devicename)
            print("DEVICEAXISES:")
            for axis in device.axislist:
                print(axis.axisname, axis.minvalue, axis.maxvalue, axis.refvalue)
        print("POSITIONS:")
        for positions in self.position_list:
            print("Positionid:", positions[0].positionsid, "number:", positions[0].positionsnumber)
            for power in positions[1]:
                print("Device", power['deviceid'], power['power'])
            for axis_position in positions[2]:
                print("Axis", self.axis_name_for_device_axisid(axis_position.deviceaxisid), "Position",
                      axis_position.position)

        print("BLOCKS:")
        for blocked in self.blocked_list:
            print("Blockvalue Axis:", blocked.axis, "Min Value:", blocked.minvalue, "Max Value", blocked.maxvalue)



if __name__ == '__main__':
    pelvi = Pelvi()
    pelvi.print_user_data()
    pelvi.move_axis_by("Y", 20)
    pelvi.move_axis_by("C", 22)
    pelvi.print_user_data()
    pelvi.add_new_user("Test", "Name")
    pelvi.move_axis_by("B", 110)
    pelvi.move_axis_to("Y", 333)
    pelvi.print_user_data()
