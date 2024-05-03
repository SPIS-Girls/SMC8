import numpy as np
import cv2

from threading import Event
from record3d import Record3DStream
from pythonosc import udp_client

import mediapipe as mp
from pose_detector import PoseDetector



class LidarApp:
    def __init__(self):
        self.event = Event()
        self.session = None
        self.DEVICE_TYPE__TRUEDEPTH = 0
        self.DEVICE_TYPE__LIDAR = 1

        self.pd = PoseDetector()
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 9999) # "192.168.1.100", 9998

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

    def get_intrinsic_mat_from_coeffs(self, coeffs):
        return np.array([[coeffs.fx,         0, coeffs.tx],
                         [        0, coeffs.fy, coeffs.ty],
                         [        0,         0,         1]])

    def calculate_depth_middle(self, depth_frame):
        center_y, center_x = np.array(depth_frame.shape) // 2 # Calculate the center of the depth array
        region = depth_frame[center_y-2:center_y+2, center_x-2:center_x+2] # Extract the 4x4 region around the center
        return np.mean(region) # Calculate the mean of the region

    def start_processing_stream(self):
        max_depth = 5 # meters, for nicer visualization
        while True:
            self.event.wait()  # Wait for new frame to arrive

            # ====== Read the newly arrived RGBD frame ======
            depth = self.session.get_depth_frame()  
            rgb = self.session.get_rgb_frame()
            # intrinsic_mat = self.get_intrinsic_mat_from_coeffs(self.session.get_intrinsic_mat())
            # camera_pose = self.session.get_camera_pose()  # Quaternion + world position (accessible via camera_pose.[qx|qy|qz|qw|tx|ty|tz])

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            detection_result = self.pd.detect(mp_image)
            wrists_left, wrists_right, torsos = self.pd.get_params()

            # ====== Calculate the distance to the middle of the depth frame and send OSC ======
            self.client.send_message("/distance", float(self.calculate_depth_middle(depth)))
            self.send_body_parts(wrists_left, wrists_right, torsos)

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

    def send_body_parts(self, wrists_left, wrists_right, torsos):
        for idx, wrist in enumerate(wrists_left):
            endpoint = "/wrists_L" + str(idx)
            self.client.send_message(endpoint, wrist)

        for idx, wrist in enumerate(wrists_right):
            endpoint = "/wrists_R" + str(idx)
            self.client.send_message(endpoint, wrist)

        for idx, torso in enumerate(torsos):
            endpoint = "/torsos" + str(idx)
            self.client.send_message(endpoint, torso)

if __name__ == '__main__':
    app = LidarApp()
    app.connect_to_device(dev_idx=0)
    try:
        app.start_processing_stream()
    except RuntimeError:
        print('Closing Client')
        