import csv
from pathlib import Path

list_of_dicts = []


file = open(Path("List.csv"))
reader = csv.reader(
    file, delimiter=',')

Header = True
for row in reader:
    if  not Header:
        dict = {
            "Hall": row[0],
            "Room": row[1],
            "Type": row[2],
            "Sqft": row[3],
            "College": row[4],
            "Region": row[5],
            "Elevator": row[6],
            "Bathroom": row[7],
            "AC": row[8],
            "Floor": row[9],
            "FilePath": row[10]
        }
        list_of_dicts.append(dict)
    else:
        Header= False

file1 = open(Path("Distance.csv"))
reader1 = csv.reader(file1, delimiter=',')

distances = []
for row1 in reader1:
    dict = {
        "Hall1": row1[0].upper(),
        "Wawa": row1[1],
        "UStore": row1[2],
        "Nassau": row1[3],
        "Jadwin Gym": row1[4],
        "Frist": row1[5],
        "Street": row1[6],
        "EQuad": row1[7],
        "Dillon": row1[8]
    }
    distances.append(dict)

for x in list_of_dicts:
    hall_name = x["Hall"].upper()
    colle_name = x["College"].upper()
    region_name = x["Region"].upper()
    for dist in distances:
        if dist["Hall1"] == hall_name:
            x.update(dist)
            break
        if dist["Hall1"] == region_name:
            x.update(dist)
            break
        if dist["Hall1"] == colle_name:
            x.update(dist)
            break

file2 = Path("masterlist.txt")
with open(file2, "w") as file1:
    file1.write("")
with open(file2, "a") as file:
    for x in list_of_dicts:
        file.write(x["Hall"])
        file.write(",")
        file.write(x["Room"])
        file.write(",")
        file.write(x["Type"])
        file.write(",")
        file.write(x["Sqft"])
        file.write(",")
        file.write(x["College"])
        file.write(",")
        file.write(x["Region"])
        file.write(",")
        file.write(x["Elevator"])
        file.write(",")
        file.write(x["Bathroom"])
        file.write(",")
        file.write(x["AC"])
        file.write(",")
        file.write(x["Floor"])
        file.write(",")
        file.write(x["FilePath"])
        file.write(",")
        file.write(x["Wawa"])
        file.write(",")
        file.write(x["UStore"])
        file.write(",")
        file.write(x["Nassau"])
        file.write(",")
        file.write(x["Jadwin Gym"])
        file.write(",")
        file.write(x["Frist"])
        file.write(",")
        file.write(x["Street"])
        file.write(",")
        file.write(x["EQuad"])
        file.write(",")
        file.write(x["Dillon"])
        file.write("\n")