from pathlib import Path
import cv2
import depthai as dai
import time

from environs import Env

env = Env()
env.read_env()

MxID = env('MxID')
# Set your custom ROI coordinates (x, y, width, height)
custom_roi = (350/640, 250/640, 640/640, 640/640)


# tiny yolo v4 label texts
labelMap = [
    "person",         "bicycle",    "car",           "motorbike",     "aeroplane",   "bus",           "train",
    "truck",          "boat",       "traffic light", "fire hydrant",  "stop sign",   "parking meter", "bench",
    "bird",           "cat",        "dog",           "horse",         "sheep",       "cow",           "elephant",
    "bear",           "zebra",      "giraffe",       "backpack",      "umbrella",    "handbag",       "tie",
    "suitcase",       "frisbee",    "skis",          "snowboard",     "sports ball", "kite",          "baseball bat",
    "baseball glove", "skateboard", "surfboard",     "tennis racket", "bottle",      "wine glass",    "cup",
    "fork",           "knife",      "spoon",         "bowl",          "banana",      "apple",         "sandwich",
    "orange",         "broccoli",   "carrot",        "hot dog",       "pizza",       "donut",         "cake",
    "chair",          "sofa",       "pottedplant",   "bed",           "diningtable", "toilet",        "tvmonitor",
    "laptop",         "mouse",      "remote",        "keyboard",      "cell phone",  "microwave",     "oven",
    "toaster",        "sink",       "refrigerator",  "book",          "clock",       "vase",          "scissors",
    "teddy bear",     "hair drier", "toothbrush"
]

nnPath = str((Path(__file__).parent / Path('model/yolov6n_coco_640x640_openvino_2022.1_6shave.blob')).resolve().absolute())

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
detectionNetwork = pipeline.create(dai.node.YoloDetectionNetwork)
objectTracker = pipeline.create(dai.node.ObjectTracker)

xlinkOut = pipeline.create(dai.node.XLinkOut)
trackerOut = pipeline.create(dai.node.XLinkOut)

xlinkOut.setStreamName("preview")
trackerOut.setStreamName("tracklets")

# Creating Manip node
manip = pipeline.create(dai.node.ImageManip)
# Setting CropRect for the Region of Interest
# manip.initialConfig.setCropRect(*custom_roi)
# Setting Resize for the neural network input size
manip.initialConfig.setResize(640, 640)
# Setting maximum output frame size based on the desired output dimensions
max_output_width = 640
max_output_height = 640
max_output_frame_size = 3 * max_output_width * max_output_height # Assuming 3 channels for BGR image
manip.setMaxOutputFrameSize(max_output_frame_size)

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
# detectionNetwork.setAnchors([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319]) #YOLOv4 uchun
# detectionNetwork.setAnchorMasks({"side26": [1, 2, 3], "side13": [3, 4, 5]})
detectionNetwork.setAnchors([10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326]) #YOLOv5 uchun
detectionNetwork.setAnchorMasks({"side52": [0,1,2], "side26": [3,4,5], "side13": [6,7,8]})
detectionNetwork.setIouThreshold(0.5)
detectionNetwork.setBlobPath(nnPath)
detectionNetwork.setNumInferenceThreads(2)
detectionNetwork.input.setBlocking(False)

objectTracker.setDetectionLabelsToTrack([0])  # track only person
# possible tracking types: ZERO_TERM_COLOR_HISTOGRAM, ZERO_TERM_IMAGELESS, SHORT_TERM_IMAGELESS, SHORT_TERM_KCF
objectTracker.setTrackerType(dai.TrackerType.ZERO_TERM_COLOR_HISTOGRAM)
# take the smallest ID when new object is tracked, possible options: SMALLEST_ID, UNIQUE_ID
objectTracker.setTrackerIdAssignmentPolicy(dai.TrackerIdAssignmentPolicy.SMALLEST_ID)

#Linking
# Connecting Manip node to ColorCamera
camRgb.preview.link(manip.inputImage)
# Connecting Manip node to YoloDetectionNetwork
manip.out.link(detectionNetwork.input)
# camRgb.preview.link(detectionNetwork.input)
objectTracker.passthroughTrackerFrame.link(xlinkOut.input)


detectionNetwork.passthrough.link(objectTracker.inputTrackerFrame)

detectionNetwork.passthrough.link(objectTracker.inputDetectionFrame)
detectionNetwork.out.link(objectTracker.inputDetections)
objectTracker.out.link(trackerOut.input)

device = dai.DeviceInfo(MxID)

# Connect to device and start pipeline
with dai.Device(pipeline, device) as device:

    preview = device.getOutputQueue("preview", 4, False)
    tracklets = device.getOutputQueue("tracklets", 4, False)

    startTime = time.monotonic()
    counter = 0
    fps = 0
    frame = None

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
        for t in trackletsData:
            if t.status.name == "TRACKED":
                roi = t.roi.denormalize(frame.shape[1], frame.shape[0])
                x1 = int(roi.topLeft().x)
                y1 = int(roi.topLeft().y)
                x2 = int(roi.bottomRight().x)
                y2 = int(roi.bottomRight().y)

                try:
                    label = labelMap[t.label]
                except:
                    label = t.label
                # if t.status.name == 'TRACKED':
                cv2.putText(frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, text_color)
                cv2.putText(frame, f"ID: {[t.id]}", (x1 + 10, y1 + 45), cv2.FONT_HERSHEY_TRIPLEX, 0.5, text_color)
                cv2.putText(frame, t.status.name, (x1 + 10, y1 + 70), cv2.FONT_HERSHEY_TRIPLEX, 0.5, text_color)
                cv2.rectangle(frame, (x1, y1), (x2, y2), rectangle, cv2.FONT_HERSHEY_SIMPLEX)

        cv2.putText(frame, "FPS: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.6, text_color)

        cv2.imshow("tracker", frame)

        if cv2.waitKey(1) == ord('q'):
            break