import requests
from environs import Env

env = Env()
env.read_env()

MxID = env('MxID')
API = env('API')

url = API + f"/camera/conf/{MxID}/"
jwt_access_token = None

def get_token(username, password):
        API = env("API")
        global jwt_access_token
        token_endpoint = f'{API}/auth/token/'
        data = {
            'username': username,
            'password': password,
        }
        try:
            response = requests.post(token_endpoint, data=data)
            if response.status_code == 200:
                jwt_access_token = response.json().get('access')
                print("Token got successfully.")
            else:
                print(f"Token get failed with status code {response.status_code}")
        except Exception as e:
            print(f"Error getting token: {e}")

def get_configurations():
    global jwt_access_token
    get_token(username=env("USERNAME", password=env("PASSWORD")))
    headers = {'Authorization': f'Bearer {jwt_access_token}'}
    response = requests.get(url, headers=headers)
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
