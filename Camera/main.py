# bible(s)
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker#configurations_options
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python#live-stream

# STEP 1: Import the necessary modules.
import numpy as np
import cv2
import mediapipe as mp
from pose_detector import PoseDetector
from pythonosc import udp_client

pd = PoseDetector()
cap = cv2.VideoCapture(0)
client = udp_client.SimpleUDPClient("127.0.0.1", 9999)

while True: 
    ret, frame = cap.read() 

    if not ret: 
        cap.release()
        cv2.destroyAllWindows()
        break
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    detection_result = pd.detect(mp_image)
    wrists_left, wrists_right, torsos = pd.get_params()

    print("left", wrists_left)
    print("right", wrists_right)
    print("torsos", torsos)

    for idx, wrist in enumerate(wrists_left):
        client.send_message("/wrists_L" + str(idx), wrist)

    for idx, wrist in enumerate(wrists_right):
        client.send_message("/wrists_R" + str(idx), wrist)

    for idx, torso in enumerate(torsos):
        client.send_message("/torsos" + str(idx), torso)


    # cv2.imshow("Video", detection_result)

    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
