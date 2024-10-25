# extract the distanceTo, AC, elevator, and
# bathroom fields for the database

import pandas as pd

def main():
    extra_info_df = pd.read_excel("ExtraRoomInfo.xlsx")

    room_info = extra_info_df.to_dict('records')
    
    print(room_info)

if __name__ == "__main__":
    main()
