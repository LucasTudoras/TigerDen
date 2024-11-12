import readCSV

rooms = readCSV.info()

with open("database.sql", 'w') as file:
    file.write('''CREATE TABLE rooms (Hall TEXT, Room TEXT, Type TEXT, Sqft INTEGER, College TEXT, Region TEXT, Elevator TEXT, Bathroom TEXT, AC TEXT, Floor INTEGER, FilePath TEXT, Wawa INTEGER, UStore INTEGER, Nassau INTEGER, JadwinGym INTEGER, Frist INTEGER, Street INTEGER, EQuad INTEGER, Dillon INTEGER, RoomID TEXT PRIMARY KEY);\n\n''')
    for room in rooms:
        file.write(f'''INSERT INTO rooms (Hall, Room, Type, Sqft, College, Region, Elevator, Bathroom, AC, Floor, FilePath, Wawa, UStore, Nassau, JadwinGym, Frist, Street, EQuad, Dillon, RoomID) VALUES ('{room["Hall"]}', '{room["Room"]}', '{room["Type"]}', '{room["Sqft"]}', '{room["College"]}', '{room["Region"]}', '{room["Elevator"]}', '{room["Bathroom"]}', '{room["AC"]}', '{room["Floor"]}', '{room["FilePath"]}', '{room["Wawa"]}', '{room["UStore"]}', '{room["Nassau"]}', '{room["Jadwin Gym"]}', '{room["Frist"]}', '{room["Street"]}', '{room["EQuad"]}', '{room["Dillon"]}', '{room["RoomID"]}');\n\n'''
        )