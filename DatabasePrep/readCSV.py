import csv
from pathlib import Path

room_info_dicts = []

# read List.csv
file = open(Path("List.csv"))
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
            "FilePath": room[10]
        }
        room_info_dicts.append(room_info)
    else:
        Header= False

# read Distance.csv
file_1 = open(Path("Distance.csv"))
hall_distances = csv.reader(file_1, delimiter=',')

# populate a list of dictionaries representing how far of a walk it is
# between a hall and various areas on campus
distances = []
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

# handle abnormal naming for halls
for room in room_info_dicts:
    hall_name = room["Hall"].upper()
    college_name = room["College"].upper()
    region_name = room["Region"].upper()
    for dist in distances:
        if dist["Hall1"] == hall_name:
            room["Wawa"] = dist["Wawa"]
            room["UStore"] = dist["UStore"]
            room["Nassau"] = dist["Nassau"]
            room["Jadwin Gym"] = dist["Jadwin Gym"]
            room["Frist"] = dist["Frist"]
            room["Street"] = dist["Street"]
            room["EQuad"] = dist["EQuad"]
            room["Dillon"] = dist["Dillon"]
            room["RoomID"] = str(room["Hall"] + room["Room"])
            break
        if dist["Hall1"] == region_name:
            room["Wawa"] = dist["Wawa"]
            room["UStore"] = dist["UStore"]
            room["Nassau"] = dist["Nassau"]
            room["Jadwin Gym"] = dist["Jadwin Gym"]
            room["Frist"] = dist["Frist"]
            room["Street"] = dist["Street"]
            room["EQuad"] = dist["EQuad"]
            room["Dillon"] = dist["Dillon"]
            room["RoomID"] = str(room["Hall"] + room["Room"])
            break
        if dist["Hall1"] == college_name:
            room["Wawa"] = dist["Wawa"]
            room["UStore"] = dist["UStore"]
            room["Nassau"] = dist["Nassau"]
            room["Jadwin Gym"] = dist["Jadwin Gym"]
            room["Frist"] = dist["Frist"]
            room["Street"] = dist["Street"]
            room["EQuad"] = dist["EQuad"]
            room["Dillon"] = dist["Dillon"]
            room["RoomID"] = str(room["Hall"] + room["Room"])
            break

# write all room information to masterlist.txt
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
