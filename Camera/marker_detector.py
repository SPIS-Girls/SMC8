import cv2 # Import the OpenCV library
import numpy as np # Import Numpy library
from time import sleep
import math

# https://chev.me/arucogen/
# REALLY IMPORTANT!
# cv2.aruco.DICT_4X4_XXX

def find_marker_by_id(list, id):
    return next((x for x in list if x['id'] == id), None)

class MarkerDetector:
    def __init__(self):
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector  = cv2.aruco.ArucoDetector(self.dictionary, self.parameters)

    def detect_raw(self, image):
        markers = []
        (corners, ids, rejected) = self.detector.detectMarkers(image)
        if ids is not None:
            ids = ids.flatten()
            for i in range(len(ids)):
                marker = {}
                center = np.mean(corners[i][0], axis=0)
                size = np.linalg.norm(corners[i][0][0] - corners[i][0][2]) / math.sqrt(2)
                marker = {'id': ids[i], 'corners': corners[i], 'center': center, "size": size}
                markers.append(marker)
        return markers
    
    def detect_rotation(self, image):
        # expected markers are 0, 1, 2, 3
        # 0-2, 1-3 complementary, in this setup
        # -  0  -
        # 3  -  1
        # -  2  -
        # angle v between 0 and 2
        # angle h between 1 and 3
        # angle ascending is 3-0 and 2-1
        # angle ascending is 0-1 and 3-2

        markers = self.detect_raw(image)

        m0 = find_marker_by_id(markers, 0)
        m1 = find_marker_by_id(markers, 1)
        m2 = find_marker_by_id(markers, 2)
        m3 = find_marker_by_id(markers, 3)

        # VERTICAL and HORIZONTAL vectors

        angle_v, angle_h = None, None

        if m0 is not None and m2 is not None:
            diff = m0['center'] - m2['center']
            vec_v = complex(diff[0], diff[1])
            angle_v = (np.angle(vec_v, deg=True) + 270) % 360

        if m1 is not None and m3 is not None:
            diff = m1['center'] - m3['center']
            vec_h = complex(diff[0], diff[1])
            angle_h = (np.angle(vec_h, deg=True) + 180) % 360

        # DIAGONAL (ascending and descending) vectors

        angle_a03, angle_a12 = None, None
        angle_d01, angle_d23 = None, None
        # to do

        # FINAL ANGLE

        angle = None

        if angle_v is not None and angle_h is not None:
            # they might be crossing the 360 to 0 threshold
            # so, if they are, we need to assume it's just one of them
            if abs(angle_v - angle_h) > 30:
                angle = angle_v
            else:
                angle = (angle_v + angle_h) / 2
        elif angle_v is not None:
            angle = angle_v
        elif angle_h is not None:
            angle = angle_h

        return angle
    

if __name__ == '__main__':
    md = MarkerDetector()
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()  
        #frame = cv2.imread('images/testaruco.png')
        frame = cv2.resize(frame, (640, 480))

        angle = md.detect_rotation(frame)

        cv2.imshow('frame', frame)
        sleep(0.2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()

dictionary = cv2.aruco.DICT_4X4_50


   