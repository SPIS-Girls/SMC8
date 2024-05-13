import numpy as np
import cv2

from threading import Event
from record3d import Record3DStream

import config
import mediapipe as mp
from pose_detector import PoseDetector
from osc_controller import OSCController
from depth_analyzer import DepthAnalyzer
from distance import Distance

class LidarApp:
    def __init__(self):
        self.event = Event()
        self.session = None
        self.DEVICE_TYPE__TRUEDEPTH = 0
        self.DEVICE_TYPE__LIDAR = 1

        self.frame_drop_counter = config.DROP_FRAME_INTERVAL
        self.detection_result = None

        self.t = 0

        self.pd = PoseDetector()
        self.oc = OSCController(config.IP, config.PORT)
        self.da = DepthAnalyzer()
        self.dis = Distance()

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
            self.dis.push_depth_frame(depth)
            is_stop = self.dis.is_on_the_floor()
            depth_middle, tilt = self.dis.get_parameters()
            # tilt = distance.calculate_tilt(depth, crunchiness)

            self.t += 1 
            # ====== Send OSC ======
            self.oc.send_distance(depth_middle) # Send the distance of the middle pixels
            self.oc.send_stop_position(is_stop) # Send the stop position
            # self.oc.send_tilt(self.one_euro_filter(self.t, tilt)) # Send the tilt

            if config.VISUALIZE:
                #  ====== Postprocess for Visualization ======
                if self.session.get_device_type() == self.DEVICE_TYPE__TRUEDEPTH:
                    depth = cv2.flip(depth, 1)
                    rgb = cv2.flip(rgb, 1)

                depth = 1 - depth / max_depth # scale depth by max_depth and invert colors

                # ====== Show the RGBD Stream ======
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
        