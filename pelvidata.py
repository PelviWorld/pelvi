from createdatabase import get_database
from user import User
from device import Device
from axis import Axis
from position import Position
from positions import Positions
from blockedarea import Blockedvalues

class Pelvidata:
    def __init__(self, name = "pelvi.db"):
        self.__database = get_database(name)

    def __get_user(self, userid):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()
        res = cur.execute("SELECT * from user where userid = :id", {'id': userid})
        data = res.fetchone()
        self.__database.commit()
        return User(data['name'], data['lastname'], data['userid'])

    def get_default_user(self):
        return self.__get_user(1)

    def __get_axis_list_from_device(self, device):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        res = cur.execute("SELECT * from deviceaxis where deviceid = :deviceid", {'deviceid': device['deviceid']})
        deviceaxis_list = res.fetchall()
        axis_list = []
        for deviceaxis in deviceaxis_list:
            res = cur.execute("SELECT * from axis where axisid = :axisid", {'axisid': deviceaxis['axisid']})
            axis = res.fetchone()
            axis_list.append(
                Axis(axis['axisid'], axis['axisname'], axis['minvalue'], axis['maxvalue'], axis['refvalue']))

        self.__database.commit()
        return axis_list

    def get_device_list(self):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        res = cur.execute("SELECT * from device")
        device_list = res.fetchall()

        devices = []
        for device in device_list:
            axis_list = self.__get_axis_list_from_device(device)
            devices.append(Device(device['deviceid'], device['devicename'],axis_list))

        self.__database.commit()
        return devices

    def __get_positions_for_positionsid(self, positionsid):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        pos_list = []

        res = cur.execute("SELECT * from position where positionsid = :positionsid", {'positionsid': positionsid})
        position_list = res.fetchall()
        for position in position_list:
            pos_list.append(Position(position['positionid'], position['positionsid'], position['deviceaxisid'], position['position']))

        self.__database.commit()
        return pos_list

    def __get_power_for_positionsid(self, positionsid):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        res = cur.execute("SELECT * from devicepower where positionsid = :positionsid", {'positionsid': positionsid})
        device_power_list = res.fetchall()

        self.__database.commit()
        return device_power_list

    def get_position_list(self, userid):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        position_list = []

        res = cur.execute("SELECT * from positions where userid = :userid", {'userid': userid})
        positions_list = res.fetchall()
        for positions in positions_list:
            pos_list = self.__get_positions_for_positionsid(positions['positionsid'])
            dev_power_list = self.__get_power_for_positionsid(positions['positionsid'])
            position_list.append([Positions(positions['positionsid'],positions['positionnumber'],positions['userid']), dev_power_list, pos_list])

        self.__database.commit()
        return position_list

    def get_blocked_list(self, userid):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        blockedarea_list = []
        res = cur.execute("SELECT * from blockedarea where userid = :userid", {'userid': userid})
        area_list = res.fetchall()
        for area in area_list:
            res = cur.execute("SELECT * from blockedvalue where blockedareaid = :blockedareaid", {'blockedareaid': area['blockedareaid']})
            blocked_list = res.fetchall()
            for value in blocked_list:
                blockedarea_list.append(Blockedvalues(value['axisid'], value['minvalue'], value['maxvalue']))

        self.__database.commit()
        return blockedarea_list

    def get_device_axis_list(self):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        res = cur.execute("SELECT * from deviceaxis")
        device_axis_list = res.fetchall()
        device_axis = {}
        for axis in device_axis_list:
            device_axis[axis['axisid']] = axis['deviceaxisid']

        res = cur.execute("SELECT * from axis")
        axis_list = res.fetchall()

        result = {}
        for axis in axis_list:
            result[device_axis[axis['axisid']]] = axis['axisname']

        self.__database.commit()
        return result

def row_dict(cursor, zeile):
    ergebnis = {}
    for spaltennr, spalte in enumerate(cursor.description):
        ergebnis[spalte[0]] = zeile[spaltennr]
    return ergebnis