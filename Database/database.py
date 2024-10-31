import csv
import sqlite3
from pathlib import Path

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('rooms.db')
cursor = conn.cursor()

# Create table to store room information
cursor.execute('''
CREATE TABLE IF NOT EXISTS rooms (
    Hall TEXT,
    Room TEXT,
    Type TEXT,
    Sqft INTEGER,
    College TEXT,
    Region TEXT,
    Elevator TEXT,
    Bathroom TEXT,
    AC TEXT,
    Floor INTEGER,
    FilePath TEXT,
    Wawa INTEGER,
    UStore INTEGER,
    Nassau INTEGER,
    JadwinGym INTEGER,
    Frist INTEGER,
    Street INTEGER,
    EQuad INTEGER,
    Dillon INTEGER,
    RoomID TEXT PRIMARY KEY
)
''')

# Read List.csv and parse room information
room_info_dicts = []

with open(Path("../DatabasePrep/List.csv")) as file:
    room_list = csv.reader(file, delimiter=',')
    header = True
    for room in room_list:
        if not header:
            room_info = {
                "Hall": room[0],
                "Room": room[1],
                "Type": room[2],
                "Sqft": room[3],
                "College": room[4],
                "Region": room[5],
                "Elevator": room[6],
                "Bathroom": room[7],
                "AC": room[8],
                "Floor": room[9],
                "FilePath": room[10]
            }
            room_info_dicts.append(room_info)
        else:
            header = False

# Read Distance.csv and populate distances
distances = []

with open(Path("../DatabasePrep/Distance.csv")) as file_1:
    hall_distances = csv.reader(file_1, delimiter=',')
    for hall in hall_distances:
        distance_to = {
            "Hall1": hall[0].upper(),
            "Wawa": hall[1],
            "UStore": hall[2],
            "Nassau": hall[3],
            "Jadwin Gym": hall[4],
            "Frist": hall[5],
            "Street": hall[6],
            "EQuad": hall[7],
            "Dillon": hall[8]
        }
        distances.append(distance_to)

# Match rooms with distances and insert into database
for room in room_info_dicts:
    hall_name = room["Hall"].upper()
    college_name = room["College"].upper()
    region_name = room["Region"].upper()
    matched_distance = None

    for dist in distances:
        if dist["Hall1"] in (hall_name, college_name, region_name):
            matched_distance = dist
            break

    if matched_distance:
        room.update({
            "Wawa": matched_distance["Wawa"],
            "UStore": matched_distance["UStore"],
            "Nassau": matched_distance["Nassau"],
            "Jadwin Gym": matched_distance["Jadwin Gym"],
            "Frist": matched_distance["Frist"],
            "Street": matched_distance["Street"],
            "EQuad": matched_distance["EQuad"],
            "Dillon": matched_distance["Dillon"],
            "RoomID": room["Hall"] + room["Room"]
        })

        # Insert data into the database
        cursor.execute('''
            INSERT OR REPLACE INTO rooms (
                Hall, Room, Type, Sqft, College, Region, Elevator, Bathroom,
                AC, Floor, FilePath, Wawa, UStore, Nassau, JadwinGym, Frist,
                Street, EQuad, Dillon, RoomID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            room["Hall"], room["Room"], room["Type"], room["Sqft"],
            room["College"], room["Region"], room["Elevator"],
            room["Bathroom"], room["AC"], room["Floor"],
            room["FilePath"], room["Wawa"], room["UStore"],
            room["Nassau"], room["Jadwin Gym"], room["Frist"],
            room["Street"], room["EQuad"], room["Dillon"],
            room["RoomID"]
        ))

# Commit and close the database connection
conn.commit()
conn.close()

print("Database created and data inserted successfully.")
