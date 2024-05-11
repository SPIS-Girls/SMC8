import cv2 # Import the OpenCV library
import numpy as np # Import Numpy library

# https://chev.me/arucogen/

class MarkerDetector:
    def __init__(self):
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector  = cv2.aruco.ArucoDetector(self.dictionary, self.parameters)

    def detect(self, image):
        cv2.imshow('1', image)
        (corners, ids, rejected) = self.detector.detectMarkers(image)
        
        return corners, ids
    
    def get_rotation(self, image):
        pass
    

if __name__ == '__main__':
    md = MarkerDetector()
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()  
        markers = md.detect(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()

dictionary = cv2.aruco.DICT_4X4_50


   