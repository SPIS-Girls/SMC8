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
cap = cv2.VideoCapture('videos/two_ppl_spinning_mid.MP4')
oc = OSCController(config.IP, config.PORT)
frame_drop_counter = config.DROP_FRAME_INTERVAL
detection_result = None

while True: 
    ret, frame = cap.read() 

    if not ret: 
        cap.release()
        cv2.destroyAllWindows()
        break
    
    # ====== Pose Detection ======
    if frame_drop_counter % config.DROP_FRAME_INTERVAL == 0:
        frame = cv2.resize(frame, (config.WIDTH, config.HEIGHT))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = pd.detect(mp_image)
        frame_drop_counter -= config.DROP_FRAME_INTERVAL
    frame_drop_counter += 1

    # ====== Send OSC ======
    oc.send_weigth_effort(pd.get_torso_calc()) # Send the weigth effort
    oc.send_body_parts(pd.get_wrist_left_calc(), pd.get_wrist_right_calc()) # Send the wrist displacement
    
    if config.VISUALIZE:
        cv2.imshow("Video", detection_result)

    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
