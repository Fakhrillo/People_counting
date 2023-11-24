from pathlib import Path
import depthai as dai

# tiny yolo v4 label texts
labelMap = ["person",]

nnPath = str((Path(__file__).parent / Path('model/yolov6n_coco_640x640_openvino_2022.1_6shave.blob')).resolve().absolute())

# Creating pipeline
pipeline = dai.Pipeline()

# Sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
detectionNetwork = pipeline.create(dai.node.YoloDetectionNetwork)
objectTracker = pipeline.create(dai.node.ObjectTracker)

# Properties
camRgb.setImageOrientation(dai.CameraImageOrientation.HORIZONTAL_MIRROR)
camRgb.setPreviewSize(640, 640)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(40)

#define a script node
script = pipeline.create(dai.node.Script)
script.setProcessor(dai.ProcessorType.LEON_CSS)

# Network specific settings
detectionNetwork.setConfidenceThreshold(0.65)
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

#Define a video encoder
videoEnc = pipeline.create(dai.node.VideoEncoder)
videoEnc.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.MJPEG)

#Linking
camRgb.preview.link(detectionNetwork.input)
camRgb.video.link(videoEnc.input)

detectionNetwork.passthrough.link(objectTracker.inputTrackerFrame)

detectionNetwork.passthrough.link(objectTracker.inputDetectionFrame)
detectionNetwork.out.link(objectTracker.inputDetections)


script.inputs['tracklets'].setBlocking(False)
script.inputs['tracklets'].setQueueSize(1)
objectTracker.out.link(script.inputs["tracklets"])

script.inputs['frame'].setBlocking(False)
script.inputs['frame'].setQueueSize(1)
videoEnc.bitstream.link(script.inputs['frame'])

script.setScript("""
import socket
import time
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 3005))
server.listen()
node.warn("Server up")
                 
trackableObjects = {}
startTime = time.monotonic()
counter = 0
fps = 0
frame = None

h_line = 380
pos = {}
going_in = 0
going_out = 0
obj_counter = [0, 0, 0, 0]  # left, right, up, down

while(True):
    conn, client = server.accept()
    node.warn(f"Connected to client IP: {client}")
    try:             
        while True:
                 
            pck = node.io["frame"].get()
            tracklets = node.io["tracklets"].tryGet()
            data = pck.getData()
            ts = pck.getTimestamp()

            counter+=1
            current_time = time.monotonic()
            if (current_time - startTime) > 1 :
                fps = counter / (current_time - startTime)
                counter = 0
                startTime = current_time
            
            trackletsData = tracklets.tracklets
            data_to_send = []
            for t in trackletsData:
                if t.status.name == "TRACKED":
                    roi = t.roi.denormalize(frame.shape[1], frame.shape[0])
                    x1 = int(roi.topLeft().x)
                    y1 = int(roi.topLeft().y)
                    x2 = int(roi.bottomRight().x)
                    y2 = int(roi.bottomRight().y)

                    # Calculate centroid
                    centroid = (int((x2-x1)/2+x1), int((y2-y1)/2+y1))
                 
                    coordinates = [x1, y1, x2, y2]

                    # Calculate the buffer zone boundaries
                    right_boundary = h_line + 15
                    left_boundary = h_line - 15

                    try:
                        if not (left_boundary <= centroid[1] <= right_boundary):
                            pos[t.id] = {
                                'previous': pos[t.id]['current'],
                                'current': centroid[1]      }
                        if pos[t.id]['current'] > right_boundary and pos[t.id]['previous'] < right_boundary:

                            obj_counter[1] += 1 #Right side
                            going_out += 1
                        if pos[t.id]['current'] < left_boundary and pos[t.id]['previous'] > left_boundary:
                            
                            obj_counter[0] += 1 #Left side
                            going_in += 1
                    except:
                        pos[t.id] = {'current': centroid[1]}

                    try:
                        label = labelMap[t.label]
                    except:
                        label = t.label
                if t.status != Tracklet.TrackingStatus.LOST and t.status != Tracklet.TrackingStatus.REMOVED:
                    text = "ID {}".format(t.id)
                 
                    data_to_send.append([text, centroid[0], centroid[1], label, coordinates, obj_counter, fps])
            
            # now to send data we need to encode it (whole header is 256 characters long)
            header = f"ABCDE " + str(ts.total_seconds()).ljust(18) + str(len(data)).ljust(8) + str(counter).ljust(16) + str(data_to_send).ljust(208) 
            conn.send(bytes(header, encoding='ascii'))
            conn.send(data)
                 
    except Exception as e:
        node.warn(f"Error oak: {e}")
        node.warn("Client disconnected")

""")

(f, bl) = dai.DeviceBootloader.getFirstAvailableDevice()
bootloader = dai.DeviceBootloader(bl)
progress = lambda p : print(f'Flashing progress: {p*100:.1f}%')
bootloader.flash(progress, pipeline)