# import depthai
# pipeline = depthai.Pipeline()

# # Create nodes, configure them and link them together

# # Upload the pipeline to the device
# with depthai.Device(pipeline) as device:
#   # Print MxID, USB speed, and available cameras on the device
#   print('MxId:',device.getDeviceInfo().getMxId())
#   print('USB speed:',device.getUsbSpeed())
#   print('Connected cameras:',device.getConnectedCameras())

#   # Input queue, to send message from the host to the device (you can receive the message on the device with XLinkIn)
#   input_q = device.getInputQueue("input_name", maxSize=4, blocking=False)

#   # Output queue, to receive message on the host from the device (you can send the message on the device with XLinkOut)
#   output_q = device.getOutputQueue("output_name", maxSize=4, blocking=False)

#   while True:
#       # Get a message that came from the queue
#       output_q.get() # Or output_q.tryGet() for non-blocking

#       # Send a message to the device
#       cfg = depthai.ImageManipConfig()
#       input_q.send(cfg)

import depthai as dai
with dai.Device() as device:
    print(device.getMxId())