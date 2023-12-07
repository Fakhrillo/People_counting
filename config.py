import requests
from environs import Env

env = Env()
env.read_env()

MxID = env('MxID')
API = env('API')

url = API + f"/camera/conf/{MxID}/"

def get_configurations():
    response = requests.get(url)
    return response.json()

try:    
    CONFIGURATIONS = get_configurations()
    DOOR_ORIENTATION = CONFIGURATIONS['Door_orientation']

    A_LINE_START_X = int(CONFIGURATIONS['A_line_start_x'])
    A_LINE_START_Y = int(CONFIGURATIONS['A_line_start_y'])
    
    A_LINE_END_X = int(CONFIGURATIONS['A_line_end_x'])
    A_LINE_END_Y = int(CONFIGURATIONS['A_line_end_y'])

    B_LINE_START_X = int(CONFIGURATIONS['B_line_start_x'])
    B_LINE_START_Y = int(CONFIGURATIONS['B_line_start_y'])

    B_LINE_END_X = int(CONFIGURATIONS['B_line_end_x'])
    B_LINE_END_Y = int(CONFIGURATIONS['B_line_end_y'])

    C_LINE_START_X = int(CONFIGURATIONS['C_line_start_x'])
    C_LINE_START_Y = int(CONFIGURATIONS['C_line_start_y'])

    C_LINE_END_X = int(CONFIGURATIONS['C_line_end_x'])
    C_LINE_END_Y = int(CONFIGURATIONS['C_line_end_y'])

except:

    DOOR_ORIENTATION = "Top"

    A_LINE_START_X = 0
    A_LINE_START_Y = 0
    
    A_LINE_END_X = 0
    A_LINE_END_Y = 0

    B_LINE_START_X = 0
    B_LINE_START_Y = 0

    B_LINE_END_X = 0
    B_LINE_END_Y = 0

    C_LINE_START_X = 0
    C_LINE_START_Y = 0

    C_LINE_END_X = 0
    C_LINE_END_Y = 0
