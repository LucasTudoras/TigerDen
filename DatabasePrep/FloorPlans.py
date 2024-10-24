# Parse through the FloorPlan folder to 
# set the floor plan to each room in the
# database

import os
import sys

FLOOR_PLAN_DIRECTORY = os.path.join(os.path.dirname(__file__), 'FloorPlan')

def read_floor_plan_path(root, file_name):
    try:
        parts = root.split(os.sep)
        college = parts[-2]
        hall = parts[-1]
        floor_name = file_name.replace(".pdf", "")

        if floor_name.isnumeric():
            floor = floor_name
        elif floor_name == 'G' or floor_name == 'A':
            floor = 0
        elif floor_name == 'Lower':
            floor = -1
        else:
            sys.exit(f"Floor plan {college}/{hall}/{floor_name} is invalid")

        return college, hall, floor
    
    except Exception as ex:
        print(f"{file_name} in {root} unsuccessful: {ex}")
        return None, None, None

def handle_floor_plans():
    floor_plans = []

    for root, dirs, files in os.walk(FLOOR_PLAN_DIRECTORY):
        for file_name in files:
            college, hall, floor = read_floor_plan_path(root, file_name)
            floor_dict = {
                'College': college,
                'Hall': hall,
                'Floor': floor,
                'FloorPlanPath': os.path.join(root, file_name)
            }
            floor_plans.append(floor_dict)
    
    return floor_plans

def write_plans(dictionaried, output_file):
    with open(output_file, 'w') as file:
        for room in dictionaried:
            file.write(f"College: {room['College']}, Hall: {room['Hall']}, Floor: {room['Floor']}, FloorPlanPath: {room['FloorPlanPath']}\n")

def main():
    dictionaried = handle_floor_plans()

    output_file = os.path.join(os.path.dirname(__file__),
        'floor_plans_paths.txt')
    
    write_plans(dictionaried, output_file)

    print("Floor plan data writted to floor_plans_path_output.txt")

if __name__ == "__main__":
    main()