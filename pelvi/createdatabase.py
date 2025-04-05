import sqlite3
from os.path import isfile, getsize

file = "pelvi.db"

def check_for_database(filename):
    if not isfile(filename):
        return False
    if getsize(filename) < 100:
        return False

    with open(filename, 'r', encoding = "ISO-8859-1") as fd:
        header = fd.read(100)
        if header.startswith('SQLite format 3'):
            return True
    return False

def create_database(connection):
    cursor = connection.cursor()
    cursor.executescript(""" 
        BEGIN;
        CREATE TABLE database (version TEXT not null);
        CREATE TABLE user (userid INTEGER primary key, name TEXT, lastname TEXT);
        CREATE TABLE rfid (rfid INTEGER primary key, userid INTEGER not null,
                     FOREIGN KEY (userid) REFERENCES user (userid));
        CREATE TABLE axis (axisid INTEGER primary key, axisname TEXT, minvalue INTEGER,
                     maxvalue INTEGER, refvalue INTEGER);
        CREATE TABLE device (deviceid INTEGER primary key, devicename TEXT);
        CREATE TABLE deviceaxis(deviceaxisid INTEGER primary key, deviceid INTEGER not null, 
                     axisid INTEGER not null,
                     FOREIGN KEY (deviceid) REFERENCES device (deviceid),
                     FOREIGN KEY (axisid) REFERENCES axis (axisid));
        CREATE TABLE positions (positionsid INTEGER primary key, userid INTEGER not null, 
                      positionnumber INTEGER, duration INTEGER, FOREIGN KEY (userid) REFERENCES user (userid));
        CREATE TABLE position (positionid INTEGER primary key, positionsid INTEGER not null,
                     deviceaxisid INTEGER not null, position INTEGER not null,
                     FOREIGN KEY (positionsid) REFERENCES positions (positionsid),
                     FOREIGN KEY (deviceaxisid) REFERENCES deviceaxis (deviceaxisid));
        CREATE TABLE devicepower(devicepowerid INTEGER primary key, positionsid INTEGER not null,
                     deviceid INTEGER not null, power INTEGER,
                     FOREIGN KEY (positionsid) REFERENCES positions (positionsid),
                     FOREIGN KEY (deviceid) REFERENCES device (deviceid));
        CREATE TABLE blockedarea(blockedareaid INTEGER primary key, userid INTEGER,
                     FOREIGN KEY (userid) REFERENCES user (userid));
        CREATE TABLE blockedvalue(blockedvalueid INTEGER primary key, blockedareaid INTEGER not null,
                     axisid INTEGER not null, minvalue INTEGER not null, maxvalue INTEGER not null,
                     FOREIGN KEY (blockedareaid) REFERENCES blockedarea (blockedareaid),
                     FOREIGN KEY (axisid) REFERENCES axis (axisid));
                      
        INSERT INTO database VALUES(1);
        COMMIT;
    """)

    # create default user
    cursor.execute("""INSERT INTO user (name, lastname) VALUES("default", "user")""")
    defaultuser = cursor.lastrowid

    # create device in Back
    cursor.execute("""INSERT INTO axis (axisname, minvalue, maxvalue, refvalue) VALUES("X", 0, 300, 0)""")
    axisx = cursor.lastrowid
    cursor.execute("""INSERT INTO axis (axisname, minvalue, maxvalue, refvalue) VALUES("Y", 0, 475, 0)""")
    axisy = cursor.lastrowid
    cursor.execute("""INSERT INTO device (devicename) VALUES("Back")""")
    deviceback = cursor.lastrowid
    cursor.execute("""INSERT INTO deviceaxis (deviceid, axisid) VALUES(?,?)""", (deviceback, axisx))
    back_device_x = cursor.lastrowid
    cursor.execute("""INSERT INTO deviceaxis (deviceid, axisid) VALUES(?,?)""", (deviceback, axisy))
    back_device_y = cursor.lastrowid

    # create device in Seat
    cursor.execute("""INSERT INTO axis (axisname, minvalue, maxvalue, refvalue) VALUES("Z", 0, 290, 0)""")
    axisz = cursor.lastrowid
    cursor.execute("""INSERT INTO axis (axisname, minvalue, maxvalue, refvalue) VALUES("E0", 0, 180, 0)""")
    axise0 = cursor.lastrowid
    cursor.execute("""INSERT INTO device (devicename) VALUES("Seat")""")
    deviceseat = cursor.lastrowid
    cursor.execute("""INSERT INTO deviceaxis (deviceid, axisid) VALUES(?,?)""", (deviceseat, axisz))
    seat_device_z = cursor.lastrowid
    cursor.execute("""INSERT INTO deviceaxis (deviceid, axisid) VALUES(?,?)""", (deviceseat, axise0))
    seat_device_e0 = cursor.lastrowid

    # create device for Leg
    cursor.execute("""INSERT INTO axis (axisname, minvalue, maxvalue, refvalue) VALUES("E1", 0, 180, 0)""")
    axise1 = cursor.lastrowid
    cursor.execute("""INSERT INTO device (devicename) VALUES("Leg")""")
    deviceleg = cursor.lastrowid
    cursor.execute("""INSERT INTO deviceaxis (deviceid, axisid) VALUES(?,?)""", (deviceleg, axise1))
    leg_device_e1 = cursor.lastrowid

    # create device for Legrest
    cursor.execute("""INSERT INTO axis (axisname, minvalue, maxvalue, refvalue) VALUES("D", 0, 1000, 0)""")
    axisd = cursor.lastrowid
    cursor.execute("""INSERT INTO device (devicename) VALUES("Legrest")""")
    devicelegrest = cursor.lastrowid
    cursor.execute("""INSERT INTO deviceaxis (deviceid, axisid) VALUES(?,?)""", (devicelegrest, axisd))
    legrest_device_d = cursor.lastrowid

    # block default back area for heart
    cursor.execute("""INSERT INTO blockedarea (userid) VALUES(?)""", (defaultuser,))
    blockedarea = cursor.lastrowid
    cursor.execute("""INSERT INTO blockedvalue (blockedareaid, axisid, minvalue, maxvalue) VALUES(?,?,?,?)""", (blockedarea, axisx, 200, 300))
    cursor.execute("""INSERT INTO blockedvalue (blockedareaid, axisid, minvalue, maxvalue) VALUES(?,?,?,?)""", (blockedarea, axisy, 50, 150))

    # set all axis to be on refvalue for default user
    cursor.execute("""INSERT INTO positions (userid, positionnumber, duration) VALUES(?,?,?)""", (defaultuser,10,0))
    positionsid = cursor.lastrowid
    cursor.execute("""INSERT INTO position (positionsid, deviceaxisid, position) VALUES(?,?,?)""", (positionsid, back_device_x, 0))
    cursor.execute("""INSERT INTO position (positionsid, deviceaxisid, position) VALUES(?,?,?)""", (positionsid, back_device_y, 0))
    cursor.execute("""INSERT INTO position (positionsid, deviceaxisid, position) VALUES(?,?,?)""", (positionsid, seat_device_z, 0))
    cursor.execute("""INSERT INTO position (positionsid, deviceaxisid, position) VALUES(?,?,?)""", (positionsid, seat_device_e0, 0))
    cursor.execute("""INSERT INTO position (positionsid, deviceaxisid, position) VALUES(?,?,?)""", (positionsid, leg_device_e1, 0))
    cursor.execute("""INSERT INTO position (positionsid, deviceaxisid, position) VALUES(?,?,?)""", (positionsid, legrest_device_d, 0))

    connection.commit()

def get_database(filename):
    db_missing = not check_for_database(filename)
    connection = sqlite3.connect(filename)
    if db_missing:
        create_database(connection)
    return connection

def zeilen_dict(cursor, zeile):
    ergebnis = {}
    for spaltennr, spalte in enumerate(cursor.description):
        ergebnis[spalte[0]] = zeile[spaltennr]
    return ergebnis

def print_version(connection):
    connection.row_factory = zeilen_dict
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM database")
    print(cursor.fetchall())
