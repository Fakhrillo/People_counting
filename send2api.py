import requests
import cv2

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
    api_url = f"{API}/camera/photo/{MxID}"
    _, img_encoded = cv2.imencode('.jpg', frame)
    response = requests.post(api_url, files={'image': (f'{MxID}.jpg', img_encoded.tobytes(), 'image/jpeg')})

    if response.status_code == 200:
        print('Image sent successfully')
    else:
        print('Error sending image to the API, status:', response.status_code)
