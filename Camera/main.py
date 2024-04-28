# bible(s)
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker#configurations_options
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python#live-stream

# STEP 1: Import the necessary modules.
import numpy as np
import cv2
import mediapipe as mp
from pose_detector import PoseDetector

# STEP 2: Create an PoseLandmarker object.
pd = PoseDetector()

# STEP 3: Load the input image.
image = mp.Image.create_from_file("image1.jpg")
# mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_frame_from_opencv)

# STEP 4: Detect pose landmarks from the input image.
detection_result = pd.detect(image)

# STEP 5: Process the detection result. In this case, visualize it.
annotated_image = PoseDetector.draw_landmarks_on_image(image.numpy_view(), detection_result)
cv2.imshow("abab", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

if len(detection_result.pose_landmarks) > 0:
    wrists_left = [[landmark[15].x, landmark[15].y, landmark[15].z] for landmark in detection_result.pose_landmarks]
    print(wrists_left)

cv2.waitKey(0)