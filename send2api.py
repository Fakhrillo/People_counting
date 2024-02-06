import requests
import cv2
from environs import Env

env = Env()
env.read_env()

jwt_access_token = None

def get_token():
        API = env("API_URL")
        global jwt_access_token
        token_endpoint = f'{API}/auth/token/'
        data = {
            'username': env("USERNAME"),
            'password': env("PASSWORD"),
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


def send_data_to_api(MxID, API, going_in, going_out):
        api_url = f'{API}/camera/result/'
        data = {
                'Cam_MxID': MxID,
                'incoming': going_in,
                'outgoing': going_out,
                }
        try:
            # Send data to the API
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, json=data, headers=headers)
            # Check if data was sent successfully
            if response.status_code == 200 or response.status_code == 201:
                return 200
            else:
                return response.status_code
        except Exception as e:
            return e
        
def send_image_to_api(API, frame, MxID):
    global jwt_access_token
    get_token()
    headers = {'Authorization': f'Bearer {jwt_access_token}'}

    api_url = f"{API}/camera/photo/{MxID}"
    _, img_encoded = cv2.imencode('.jpg', frame)
    response = requests.post(api_url, files={'image': (f'{MxID}.jpg', img_encoded.tobytes(), 'image/jpeg')}, headers=headers)

    if response.status_code == 200:
        print('Image sent successfully')
    else:
        print('Error sending image to the API, status:', response.status_code)
