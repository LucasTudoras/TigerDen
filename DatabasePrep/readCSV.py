import csv
from pathlib import Path

room_info_dicts = []

# read List.csv
file = open("/Users/lakeguy848/Desktop/Cos333 final/TigerDen/DatabasePrep/Master.csv")
room_list = csv.reader(file, delimiter=',')

# iterate through every room to parse its information
Header = True
for room in room_list:
    # skip the first row of List.csv
    if not Header:
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
            "FilePath": room[10],
            "Wawa": room[11],
            "UStore": room[12],
            "Nassau": room[13],
            "Jadwin Gym": room[14],
            "Frist": room[15],
            "Street": room[16],
            "EQuad": room[17],
            "Dillon": room[18],
            "RoomID": room[19]
        }
        room_info_dicts.append(room_info)
    else:
        Header= False


# write all room information to masterlist.txt
def write_to_file():
    file_2 = Path("masterlist.txt")
    with open(file_2, "w") as file1:
        file1.write("")
    with open(file_2, "a") as file:
        for room in room_info_dicts:
            file.write(room["Hall"])
            file.write(",")
            file.write(room["Room"])
            file.write(",")
            file.write(room["Type"])
            file.write(",")
            file.write(room["Sqft"])
            file.write(",")
            file.write(room["College"])
            file.write(",")
            file.write(room["Region"])
            file.write(",")
            file.write(room["Elevator"])
            file.write(",")
            file.write(room["Bathroom"])
            file.write(",")
            file.write(room["AC"])
            file.write(",")
            file.write(room["Floor"])
            file.write(",")
            file.write(room["FilePath"])
            file.write(",")
            file.write(room["Wawa"])
            file.write(",")
            file.write(room["UStore"])
            file.write(",")
            file.write(room["Nassau"])
            file.write(",")
            file.write(room["Jadwin Gym"])
            file.write(",")
            file.write(room["Frist"])
            file.write(",")
            file.write(room["Street"])
            file.write(",")
            file.write(room["EQuad"])
            file.write(",")
            file.write(room["Dillon"])
            file.write(",")
            file.write(room["RoomID"])
            file.write("\n")

def info():
    return room_info_dicts