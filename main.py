from pathlib import Path
import cv2
import depthai as dai
import time
import requests
from environs import Env
import numpy as np

from count import counting_people
from draw_line import drawline
from http_streaming import server_HTTP

env = Env()
env.read_env()

MxID = env('MxID')
IP = env('IP')
# API = env('API')

# door = ['bottom', 'top', 'left', 'right']
door = "bottom"

# Coordinates of the counting line
# First camera, above window
# A_start = (150, 130)
# A_end = (150, 400)

# B_start = (400, 130)
# B_end = (400, 400)

# C_start = (400, 400)
# C_end = (150, 400)

A_start = (130, 300)
A_end = (130, 500)

B_start = (550, 300)
B_end = (550, 500)

C_start = (130, 300)
C_end = (550, 300)

# Second camera, above door
# #BOTTOM 
# A_start = (130, 300)
# A_end = (130, 500)

# B_start = (550, 300)
# B_end = (550, 500)

# C_start = (130, 300)
# C_end = (550, 300)

# #TOP
# A_start = (130, 60)
# A_end = (130, 300)

# B_start = (550, 60)
# B_end = (550, 300)

# C_start = (130, 300)
# C_end = (550, 300)

# tiny yolo v4 label texts
labelMap = ["person",]

nnPath = str((Path(__file__).parent / Path('model/yolov6n_coco_640x640_openvino_2022.1_6shave.blob')).resolve().absolute())

# Creating pipeline
pipeline = dai.Pipeline()

# Sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
detectionNetwork = pipeline.create(dai.node.YoloDetectionNetwork)
objectTracker = pipeline.create(dai.node.ObjectTracker)

xlinkOut   = pipeline.create(dai.node.XLinkOut)
trackerOut = pipeline.create(dai.node.XLinkOut)

xlinkOut.setStreamName("preview")
trackerOut.setStreamName("tracklets")

# Properties
if MxID == "14442C10C1AD3FD700":
    camRgb.setImageOrientation(dai.CameraImageOrientation.HORIZONTAL_MIRROR)
camRgb.setPreviewSize(640, 640)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(40)

# Network specific settings
detectionNetwork.setConfidenceThreshold(0.5)
detectionNetwork.setNumClasses(80)
detectionNetwork.setCoordinateSize(4)
# detectionNetwork.setAnchors([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319]) #for YOLOv4
# detectionNetwork.setAnchorMasks({"side26": [1, 2, 3], "side13": [3, 4, 5]})
detectionNetwork.setAnchors([10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326]) #for YOLOv5
detectionNetwork.setAnchorMasks({"side52": [0,1,2], "side26": [3,4,5], "side13": [6,7,8]})
detectionNetwork.setIouThreshold(0.5)
detectionNetwork.setBlobPath(nnPath)
detectionNetwork.setNumInferenceThreads(2)
detectionNetwork.input.setBlocking(False)

objectTracker.setDetectionLabelsToTrack([0])  # track only person
# possible tracking types: ZERO_TERM_COLOR_HISTOGRAM, ZERO_TERM_IMAGELESS, SHORT_TERM_IMAGELESS, SHORT_TERM_KCF
objectTracker.setTrackerType(dai.TrackerType.ZERO_TERM_COLOR_HISTOGRAM)
# take the smallest ID when new object is tracked, possible options: SMALLEST_ID, UNIQUE_ID
objectTracker.setTrackerIdAssignmentPolicy(dai.TrackerIdAssignmentPolicy.UNIQUE_ID)

#Linking
camRgb.preview.link(detectionNetwork.input)
objectTracker.passthroughTrackerFrame.link(xlinkOut.input)

detectionNetwork.passthrough.link(objectTracker.inputTrackerFrame)

detectionNetwork.passthrough.link(objectTracker.inputDetectionFrame)
detectionNetwork.out.link(objectTracker.inputDetections)
objectTracker.out.link(trackerOut.input)

device = dai.DeviceInfo(MxID)
# device = dai.DeviceInfo(IP)

print(device)

# Connecting to device and starting pipeline
with dai.Device(pipeline, device) as device:

    preview = device.getOutputQueue("preview", 4, False)
    tracklets = device.getOutputQueue("tracklets", 4, False)

    startTime = time.monotonic()
    counter = 0
    fps = 0
    frame = None

    # def send_to_api(MxID, going_in, going_out):
    #     api_url = f'{API}/camera/result/'
    #     data = {
    #             'mxid': MxID,
    #             'incoming': going_in,
    #             'outgoing': going_out,}
    #     try:
    #         # Send data to the API
    #         headers = {'Content-Type': 'application/json'}
    #         response = requests.post(api_url, json=data, headers=headers)
    #         # Check if data was sent successfully
    #         if response.status_code == 200 or response.status_code == 201:
    #             return 200
    #         else:
    #             return response.status_code
    #     except Exception as e:
    #         return e

    pos = {}
    going_in = 0
    going_out = 0
    obj_counter = [0, 0, 0, 0]  # left, right, up, down
    image_saved = False
    frame_count = 0
    last_print_time = 0

    while(True):
        imgFrame = preview.get()
        track = tracklets.get()

        counter+=1
        current_time = time.monotonic()
        if (current_time - startTime) > 1 :
            fps = counter / (current_time - startTime)
            counter = 0
            startTime = current_time

        color = (255, 0, 0)
        text_color = (0, 0, 255)
        rectangle = (111, 147, 26)

        frame = imgFrame.getCvFrame()
        trackletsData = track.tracklets

        # Send the image to the API after processing a certain number of frames
        # if not image_saved and frame_count >= 25:
        #     api_url = f"{API}/camera/photo/{MxID}"
        #     _, img_encoded = cv2.imencode('.jpg', frame)  # Encode the image as JPEG
        #     response = requests.post(api_url, files={'image': (f'{MxID}.jpg', img_encoded.tobytes(), 'image/jpeg')})

        #     # Check the response from the API
        #     if response.status_code == 200:
        #         print('Image sent successfully')
        #         image_saved = True
        #     else:
        #         print('Error sending image to the API, status:', response.status_code)

        # if frame_count <= 30:
        #     frame_count += 1

        # Draw the counting line on the frame
        cv2.line(frame, A_start, A_end, (0, 0, 255), 3)
        cv2.line(frame, B_start, B_end, (0, 255, 0), 3)
        cv2.line(frame, C_start, C_end, (255, 0, 0), 3)

        # Calculate the buffer zone boundaries
        A_right_boundary = A_start[0] + 25
        A_left_boundary = A_start[0] - 25
        A_max = A_end[1]
        A_min = A_start[1]

        B_right_boundary = B_start[0] +25
        B_left_boundary = B_start[0] - 25
        B_max = B_end[1]
        B_min = B_start[1]


        C_right_boundary = C_start[1] + 25
        C_left_boundary = C_start[1] - 25
        C_max = C_end[0]
        C_min = C_start[0]

        for t in trackletsData:
            if t.status.name == "TRACKED":
                roi = t.roi.denormalize(frame.shape[1], frame.shape[0])
                x1 = int(roi.topLeft().x)
                y1 = int(roi.topLeft().y)
                x2 = int(roi.bottomRight().x)
                y2 = int(roi.bottomRight().y)

                # Calculate centroid
                centroid = (int((x2-x1)/2+x1), int((y2-y1)/2+y1))

                try:
                    # if door == "bottom":
                    #     if not (C_left_boundary <= centroid[1] <= C_right_boundary and C_min <= centroid[1] <= C_max or A_left_boundary <= centroid[0] <= A_right_boundary and A_min <= centroid[0] <= A_max or B_left_boundary <= centroid[0] <= B_left_boundary and B_min <= centroid[0] <= B_max):
                    #         pos[t.id] = {
                    #             'previous': pos[t.id]['current'],
                    #             'current': centroid[1]      }
                            
                    #     if pos[t.id]['current'] > C_right_boundary > pos[t.id]['previous'] and C_max > centroid[0] > C_min or pos[t.id]['current'] > A_right_boundary > pos[t.id]['previous'] and A_max > centroid[1] > A_min or pos[t.id]['current'] < B_right_boudary < pos[t.id]['previous'] and B_max > centroid[1] > B_min:

                    #         obj_counter[1] += 1 #Right side
                    #         going_out += 1
                    #     if pos[t.id]['current'] < C_left_boundary < pos[t.id]['previous'] and C_max > centroid[0] > C_min or pos[t.id]['current'] < A_right_boundary < pos[t.id]['previous'] and A_max > centroid[1] > A_min or pos[t.id]['current'] > B_right_boudary > pos[t.id]['previous'] and B_max > centroid[1] > B_min:
                            
                    #         obj_counter[0] += 1 #Left side
                    #         going_in += 1

                    counting_people(door, centroid, pos, t, obj_counter, C_left_boundary, C_right_boundary, C_min, C_max, A_left_boundary, A_right_boundary, A_min, A_max, B_left_boundary, B_right_boundary, B_min, B_max)    
                except:
                    pos[t.id] = {'current': centroid[1]}

                try:
                    label = labelMap[t.label]
                except:
                    label = t.label

                cv2.putText(frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, text_color)
                cv2.putText(frame, f"ID: {[t.id]}", (x1 + 10, y1 + 45), cv2.FONT_HERSHEY_TRIPLEX, 0.5, text_color)
                cv2.putText(frame, t.status.name, (x1 + 10, y1 + 70), cv2.FONT_HERSHEY_TRIPLEX, 0.5, text_color)
                cv2.rectangle(frame, (x1, y1), (x2, y2), rectangle, cv2.FONT_HERSHEY_SIMPLEX)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (255, 255, 255), -1)
        
        drawline(frame, (A_right_boundary, A_start[1]), (A_right_boundary, A_end[1]), text_color, 2, 'line')
        drawline(frame, (A_left_boundary, A_start[1]), (A_left_boundary, A_end[1]), text_color, 2, 'line')
        
        drawline(frame, (B_right_boundary, B_start[1]), (B_right_boundary, B_end[1]), text_color, 2, 'line')
        drawline(frame, (B_left_boundary, B_start[1]), (B_left_boundary, B_end[1]), text_color, 2, 'line')
        
        drawline(frame, (C_start[0], C_right_boundary), (C_end[0], C_right_boundary), text_color, 2, 'line')
        drawline(frame, (C_start[0], C_left_boundary), (C_end[0], C_left_boundary), text_color, 2, 'line')

        # current_time = time.time()
        # if current_time - last_print_time >= 300:
        #     last_print_time = current_time
        #     result = send_to_api(MxID, going_in, going_out)
        #     if result == 200:
        #         print(f'Data sent successfully, status: {result},  {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}', )
        #         going_in = 0
        #         going_out = 0
        #     else:
        #         print(f'Error sending data to the API, status: {result}')

        cv2.putText(frame, f'Kirdi: {obj_counter[0]}; Chiqdi: {obj_counter[1]} Xonada bor: {obj_counter[0] - obj_counter[1]}', (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0xFF), 2, cv2.FONT_HERSHEY_SIMPLEX)
        cv2.putText(frame, "FPS: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.6, text_color)

        # Displaying cropped frame with tracked objects
        cv2.imshow("tracker", frame)
        server_HTTP.frametosend = frame

        if cv2.waitKey(1) == ord('q'):
            break