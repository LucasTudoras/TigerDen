# Parse through the Extra Room Info 
# Google Sheets to extract the 
# distanceTo, AC, elevator, and
# bathroom fields for the database

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

EXTRA_INFO_PATH = (insertfilepath.envhere)

extra_info_db = pd.read_excel(EXTRA_INFO_PATH)

# Loop through each room to get its extra 
# info and put this into a dictionary 