from pelvi.createdatabase import get_database
from pelvi.user import User
from pelvi.device import Device
from pelvi.axis import Axis
from pelvi.position import Position
from pelvi.positions import Positions
from pelvi.blockedarea import Blockedvalues

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

    def load_user(self, name, lastname):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        res = cur.execute("SELECT * from user where name like :name and lastname like :lastname", {'name': name, 'lastname': lastname})
        if not res.fetchall():
            return 1

        userid = res.lastrowid

        self.__database.commit()
        return userid

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
            position_list.append([Positions(positions['positionsid'],positions['positionnumber'],positions['duration'],positions['userid']),
                                  dev_power_list, pos_list])

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
                blockedarea_list.append(Blockedvalues(value['axisid'], value['minvalue'], value['maxvalue'], value['blockedvalueid']))

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

    def check_user_name_not_in_use(self, name, lastname):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        res = cur.execute("SELECT * from user where name like :name and lastname like :lastname", {'name': name, 'lastname': lastname})

        self.__database.commit()
        if not res.fetchall():
            return True
        return False

    def add_user(self, name, lastname):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        cur.execute("""INSERT INTO user (name, lastname) VALUES(?, ?)""", (name, lastname))
        userid = cur.lastrowid

        self.__database.commit()
        return userid

    def update_user(self, user):
        if user.userid == -1:
            self.add_user(user.name, user.lastname)
            return

        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        cur.execute("""UPDATE user SET name = :name, lastname = :lastname WHERE userid = :userid""",
                    {'name': user.name, 'lastname': user.lastname, 'userid': user.userid})

        self.__database.commit()

    def add_positions_head(self, position):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        cur.execute("""INSERT INTO positions (userid, positionnumber, duration) VALUES(?,?,?)""",
                    (position.userid, position.positionsnumber, position.duration))
        positionsid = cur.lastrowid

        self.__database.commit()
        return positionsid

    def update_positions_head(self, positions):
        if positions.positionsid == -1:
            return self.add_positions_head(positions)
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        cur.execute("""UPDATE positions SET positionnumber = :positionnumber, duration = :duration WHERE positionsid = :positionsid""",
                    {'positionnumber': positions.positionsnumber, 'duration': positions.duration, 'positionsid': positions.positionsid})
        positionsid = cur.lastrowid

        self.__database.commit()
        return positionsid

    def add_position(self, position):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        cur.execute("""INSERT INTO position (positionsid, deviceaxisid, position) VALUES(?,?,?)""",
                       (position.positionsid, position.deviceaxisid, position.position))
        positionid = cur.lastrowid
        position.positionid = positionid

        self.__database.commit()

    def update_position(self, position):
        if position.positionid == -1:
            self.add_position(position)
            return

        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        cur.execute("""UPDATE position SET positionsid = :positionsid, deviceaxisid = :deviceaxisid, position = :position WHERE positionid = :positionid""",
                    {'positionsid': position.positionsid, 'deviceaxisid': position.deviceaxisid, 'position': position.position, 'positionid': position.positionid})

    def add_blocked_area_head(self, userid):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        cur.execute("""INSERT INTO blockedarea (userid) VALUES(?)""", (userid,))
        blockedareaid = cur.lastrowid

        self.__database.commit()
        return blockedareaid

    def add_blocked_area(self, userid, blocked):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        blockedareaid = self.add_blocked_area_head(userid)
        for blockedvalue in blocked:
            cur.execute("""INSERT INTO blockedvalue (blockedareaid, axisid, minvalue, maxvalue) VALUES (?,?,?,?)""",
                        (blockedareaid, blockedvalue.axis, blockedvalue.minvalue, blockedvalue.maxvalue))
            blockedvalueid = cur.lastrowid
            blockedvalue.blockedvalueid = blockedvalueid

        self.__database.commit()

    def update_blocked_area(self, userid, blocked):
        self.__database.row_factory = row_dict
        cur = self.__database.cursor()

        for blockedvalue in blocked:
            cur.execute("""UPDATE blockedvalue SET axisid = :axisid, minvalue = :minvalue, maxvalue = :maxvalue WHERE blockedvalueid = :blockedvalueid""",
                        {'axisid': blockedvalue.axis, 'minvalue': blockedvalue.minvalue, 'maxvalue': blockedvalue.maxvalue, 'blockedvalueid': blockedvalue.blockedvalueid})

        self.__database.commit()

    def save_user_data(self, user, position_list, blocked_list):
        self.update_user(user)
        for position in position_list:
            positionsid = self.update_positions_head(position[0])
            for pos in position[2]:
                self.update_position(pos)
        self.update_blocked_area(user.userid, blocked_list)


def row_dict(cursor, zeile):
    ergebnis = {}
    for spaltennr, spalte in enumerate(cursor.description):
        ergebnis[spalte[0]] = zeile[spaltennr]
    return ergebnis