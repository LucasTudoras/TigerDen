import csv
from pathlib import Path

list_of_dicts = []

file = open(Path("List.csv"))
reader = csv.reader(file, delimiter=',')

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
    else:
        Header= False

