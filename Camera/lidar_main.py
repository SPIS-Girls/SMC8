import numpy as np
import cv2

from threading import Event
from record3d import Record3DStream

import config
import mediapipe as mp
from pose_detector import PoseDetector
from osc_controller import OSCController


class LidarApp:
    def __init__(self):
        self.event = Event()
        self.session = None
        self.DEVICE_TYPE__TRUEDEPTH = 0
        self.DEVICE_TYPE__LIDAR = 1

        self.pd = PoseDetector()
        self.oc = OSCController(config.IP, config.PORT)

    def on_new_frame(self):
        """
        This method is called from non-main thread, therefore cannot be used for presenting UI.
        """
        self.event.set()  # Notify the main thread to stop waiting and process new frame.

    def on_stream_stopped(self):
        raise RuntimeError('Stream stopped') 

    def connect_to_device(self, dev_idx):
        print('Searching for devices')
        devs = Record3DStream.get_connected_devices()
        print('{} device(s) found'.format(len(devs)))
        for dev in devs:
            print('\tID: {}\n\tUDID: {}\n'.format(dev.product_id, dev.udid))

        if len(devs) <= dev_idx:
            raise RuntimeError('Cannot connect to device #{}, try different index.'
                               .format(dev_idx))

        dev = devs[dev_idx]
        self.session = Record3DStream()
        self.session.on_new_frame = self.on_new_frame
        self.session.on_stream_stopped = self.on_stream_stopped
        self.session.connect(dev)  # Initiate connection and start capturing

    def start_processing_stream(self):
        max_depth = 5 # meters, for nicer visualization
        while True:
            self.event.wait()  # Wait for new frame to arrive

            # ====== Read the newly arrived RGBD frame ======
            depth = self.session.get_depth_frame()  
            rgb = self.session.get_rgb_frame()

            # ====== Depth Calucaltions ======
            depth_middle = float(self.calculate_depth_middle(depth))
            # TODO Giacomo's code

            # ====== Pose Detection ======
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            detection_result = self.pd.detect(mp_image)
            wrists_left, wrists_right, torsos = self.pd.get_params()

            # ====== Send OSC ======
            self.oc.send_distance(depth_middle) # Send the distance of the middle pixels
            self.oc.send_body_parts(wrists_left, wrists_right, torsos) # Send the body parts

            if config.VISUALIZE:
                #  ====== Postprocess for Visualization ======
                if self.session.get_device_type() == self.DEVICE_TYPE__TRUEDEPTH:
                    depth = cv2.flip(depth, 1)
                    rgb = cv2.flip(rgb, 1)

                detection_result = cv2.cvtColor(detection_result, cv2.COLOR_RGB2BGR)
                rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                depth = 1 - depth / max_depth # scale depth by max_depth and invert colors

                # ====== Show the RGBD Stream ======
                cv2.imshow("Pose Detection", detection_result)
                cv2.imshow('Depth', depth)            
                cv2.waitKey(1)  # Needed to refresh the window

            self.event.clear()

if __name__ == '__main__':
    app = LidarApp()
    app.connect_to_device(dev_idx=0)
    try:
        app.start_processing_stream()
    except RuntimeError:
        print('Closing Client')
        