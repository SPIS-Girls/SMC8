# bible(s)
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker#configurations_options
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python#live-stream

# STEP 1: Import the necessary modules.
import numpy as np
import cv2
import config
import mediapipe as mp
from pose_detector import PoseDetector
from pythonosc import udp_client
from osc_controller import OSCController

pd = PoseDetector()
cap = cv2.VideoCapture(0)
oc = OSCController(config.IP, config.PORT)

while True: 
    ret, frame = cap.read() 

    if not ret: 
        cap.release()
        cv2.destroyAllWindows()
        break
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    detection_result = pd.detect(mp_image)

    oc.send_weigth_effort(pd.get_torso_calc()) # Send the weigth effort
    oc.send_body_parts(pd.get_wrist_left_calc(), pd.get_wrist_right_calc()) # Send the body parts
    oc.send_rotation(pd.get_rotation_calc()) # Send the rotation

    print("torso", pd.get_torso_calc())
    print("rotation", pd.get_rotation_calc())
    print("wrists left", pd.get_wrist_left_calc())
    print("wrists right", pd.get_wrist_right_calc())

    
    if config.VISUALIZE:
        cv2.imshow("Video", detection_result)

    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
