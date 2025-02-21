from pathlib import Path
import cv2
import depthai as dai
import time
from environs import Env
from threading import Thread

from count import *
from send2api import *
# from http_streaming import server_HTTP

env = Env()
env.read_env()

MxID = env('MxID')
API = env('API')

from config import (
    DOOR_ORIENTATION,

    A_LINE_START_X,
    A_LINE_START_Y,
    
    A_LINE_END_X,
    A_LINE_END_Y,

    B_LINE_START_X,
    B_LINE_START_Y,

    B_LINE_END_X,
    B_LINE_END_Y,

    C_LINE_START_X,
    C_LINE_START_Y,

    C_LINE_END_X,
    C_LINE_END_Y,
)

# nnPath = str((Path(__file__).parent / Path('model/yolov6n_coco_640x640_openvino_2022.1_6shave.blob')).resolve().absolute())
nnPath = str((Path(__file__).parent / Path('model/Yolov6n_100epoch_openvino_2022.1_6shave.blob')).resolve().absolute())

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

# Network specific settings
detectionNetwork.setConfidenceThreshold(0.5)
detectionNetwork.setNumClasses(2)
detectionNetwork.setCoordinateSize(4)
# detectionNetwork.setAnchors([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319]) #for YOLOv4
# detectionNetwork.setAnchorMasks({"side26": [1, 2, 3], "side13": [3, 4, 5]})
detectionNetwork.setAnchors([10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326]) #for YOLOv5
detectionNetwork.setAnchorMasks({"side52": [0,1,2], "side26": [3,4,5], "side13": [6,7,8]})
detectionNetwork.setIouThreshold(0.5)
detectionNetwork.setBlobPath(nnPath)
detectionNetwork.setNumInferenceThreads(2)
detectionNetwork.input.setBlocking(False)

objectTracker.setDetectionLabelsToTrack([1])  # track only person
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

# Connecting to device and starting pipeline
with dai.Device(pipeline, device) as device:

    preview = device.getOutputQueue("preview", 4, False)
    tracklets = device.getOutputQueue("tracklets", 4, False)

    startTime = time.monotonic()
    counter = 0
    fps = 0
    frame = None

    pos = {}
    count_in_out = [0, 0]
    obj_counter = [0, 0, 0, 0]  # left, right, up, down
    image_saved = False
    frame_count = 0
    last_print_time = 0

    color = (255, 0, 0)
    text_color = (0, 0, 255)
    rectangle = (111, 147, 26)
    boundary = 40

    # Calculate the buffer zone boundaries
    if DOOR_ORIENTATION in ["Top", "Bottom"]:
        A_right_boundary = A_LINE_START_X + boundary
        A_left_boundary = A_LINE_START_X - boundary
        A_max = A_LINE_END_Y
        A_min = A_LINE_START_Y

        B_right_boundary = B_LINE_START_X + boundary
        B_left_boundary = B_LINE_START_X - boundary
        B_max = B_LINE_END_Y
        B_min = B_LINE_START_Y

        C_right_boundary = C_LINE_START_Y + boundary
        C_left_boundary = C_LINE_START_Y - boundary
        C_max = C_LINE_END_X
        C_min = C_LINE_START_X

    elif DOOR_ORIENTATION in['Right', 'Left']:
        A_right_boundary = A_LINE_START_Y + boundary
        A_left_boundary = A_LINE_START_Y - boundary
        A_max = A_LINE_END_X
        A_min = A_LINE_START_X

        B_right_boundary = B_LINE_START_Y + boundary
        B_left_boundary = B_LINE_START_Y - boundary
        B_max = B_LINE_END_X
        B_min = B_LINE_START_X

        C_right_boundary = C_LINE_START_X + boundary
        C_left_boundary = C_LINE_START_X - boundary
        C_max = C_LINE_END_Y
        C_min = C_LINE_START_Y

    else:
        print(f"Door orientation is not supported: {DOOR_ORIENTATION}")

    def get_count_function(orientation):
        if orientation == 'Top':
            return door_top
        elif orientation == 'Bottom':
            return door_bottom
        elif orientation == 'Right':
            return door_right
        elif orientation == 'Left':
            return door_left
        else:
            raise ValueError("Invalid orientation")

    counting_people = get_count_function(DOOR_ORIENTATION)
    startingTime = time.strftime("%Y-%m-%d %H:%M", time.localtime())

    while(True):
        imgFrame = preview.get()
        track = tracklets.get()

        counter+=1
        current_time = time.monotonic()
        if (current_time - startTime) > 1 :
            fps = counter / (current_time - startTime)
            counter = 0
            startTime = current_time

        frame = imgFrame.getCvFrame()
        trackletsData = track.tracklets

        # Send the image to the API after processing a certain number of frames
        if not image_saved and frame_count >= 25:
            # Start a new thread for sending the image
            send_thread = Thread(target=send_image_to_api, args=(API, frame.copy(), MxID))
            send_thread.start()

            # Continue processing the next frame
            image_saved = True

        if frame_count <= 30:
            frame_count += 1

        # Draw the counting line on the frame
        cv2.line(frame, (A_LINE_START_X, A_LINE_START_Y), (A_LINE_END_X, A_LINE_END_Y), (0, 0, 255), 3)
        cv2.line(frame, (B_LINE_START_X, B_LINE_START_Y), (B_LINE_END_X, B_LINE_END_Y), (0, 255, 0), 3)
        cv2.line(frame, (C_LINE_START_X, C_LINE_START_Y), (C_LINE_END_X, C_LINE_END_Y), (255, 0, 0), 3)

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
                    
                    counting_people(centroid, pos, t, obj_counter, count_in_out, C_left_boundary, C_right_boundary, C_min, C_max, A_left_boundary, A_right_boundary, A_min, A_max, B_left_boundary, B_right_boundary, B_min, B_max)    

                except:
                    pos[t.id] = {'current': centroid}

                cv2.putText(frame, f"ID: {[t.id]}", (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, text_color)
                cv2.putText(frame, t.status.name, (x1 + 10, y1 + 45), cv2.FONT_HERSHEY_TRIPLEX, 0.5, text_color)
                cv2.rectangle(frame, (x1, y1), (x2, y2), rectangle, cv2.FONT_HERSHEY_SIMPLEX)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (255, 255, 255), -1)

        current_time = time.time()
        if current_time - last_print_time >= 300:
            last_print_time = current_time
            result = send_data_to_api(MxID, API, count_in_out[0], count_in_out[1])
            print(f"IN: {count_in_out[0]}, OUT: {count_in_out[1]}")
            if result == 200:
                print(f'Data sent successfully, status: {result},  {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}', )
                count_in_out[0] = 0
                count_in_out[1] = 0
            else:
                print(f'Error sending data to the API, status: {result}')

        cv2.putText(frame, f'In: {obj_counter[0]}; Out: {obj_counter[1]} Present: {obj_counter[0] - obj_counter[1]}', (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0xFF), 2, cv2.FONT_HERSHEY_SIMPLEX)
        cv2.putText(frame, f"ST: {startingTime}", (frame.shape[1] - 300, 35), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 255, 0))
        cv2.putText(frame, "FPS: {:.2f}".format(fps), (2, frame.shape[0] - 10), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255, 0, 0))

        # Displaying cropped frame with tracked objects
        cv2.imshow("tracker", frame)
        # server_HTTP.frametosend = frame

        if cv2.waitKey(1) == ord('q'):
            break