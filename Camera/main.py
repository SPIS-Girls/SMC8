# bible(s)
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker#configurations_options
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python#live-stream

# STEP 1: Import the necessary modules.
import numpy as np
import cv2
import mediapipe as mp
from pose_detector import PoseDetector

pd = PoseDetector()
cap = cv2.VideoCapture(0)

while True: 
    ret, frame = cap.read() 

    if not ret: 
        cap.release()
        cv2.destroyAllWindows()
        break
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    detection_result = pd.detect(mp_image)

    cv2.imshow("Video", detection_result)

    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
