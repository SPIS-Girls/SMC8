import cv2 # Import the OpenCV library
import numpy as np # Import Numpy library
from time import sleep, time
import math

# https://chev.me/arucogen/
# REALLY IMPORTANT!
# cv2.aruco.DICT_4X4_XXX

def find_marker_by_id(list, id):
    return next((x for x in list if x['id'] == id), None)

def two_angles_average(angles):

    count = len(angles)
    if count != 2:
        return None
        
    min = np.min(angles)
    max = np.max(angles)
    if max > min + 180:
        min += 360
    avg = ((min + max) / 2) % 360

    return avg

class MarkerDetector:
    def __init__(self):
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector  = cv2.aruco.ArucoDetector(self.dictionary, self.parameters)
        self.old_angle_result = None
        self.old_time = time()

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
    
    def detect_angle(self, image):

        # expected markers are 0, 1, 2, 3
        # -  0  -
        # 3  -  1
        # -  2  -
        # angle v between 0-2
        # angle h between 1-3
        # angle ascending is 3-0 or 2-1
        # angle ascending is 0-1 or 3-2

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

        angle_asc = None

        if m3 is not None and m0 is not None:
            diff = m3['center'] - m0['center']
            vec_asc = complex(diff[0], diff[1])
            angle_asc = (np.angle(vec_asc, deg=True) + 45) % 360
        elif m2 is not None and m1 is not None:
            diff = m2['center'] - m1['center']
            vec_asc = complex(diff[0], diff[1])
            angle_asc = (np.angle(vec_asc, deg=True) + 45) % 360
        
        angle_des = None

        if m0 is not None and m1 is not None:
            diff = m0['center'] - m1['center']
            vec_des = complex(diff[0], diff[1])
            angle_des = (np.angle(vec_des, deg=True) + 315) % 360
        elif m3 is not None and m2 is not None:
            diff = m3['center'] - m2['center']
            vec_des = complex(diff[0], diff[1])
            angle_des = (np.angle(vec_des, deg=True) + 315) % 360

        # FINAL ANGLE

        cardinal_angle = None

        if angle_v is not None and angle_h is not None:
            cardinal_angle = two_angles_average([angle_v, angle_h])
        elif angle_v is not None:
            cardinal_angle = angle_v
        elif angle_h is not None:
            cardinal_angle = angle_h

        diagonal_angle = None

        if angle_asc is not None and angle_des is not None:
            diagonal_angle = two_angles_average([angle_asc, angle_des])
        elif angle_asc is not None:
            diagonal_angle = angle_asc
        elif angle_des is not None:
            diagonal_angle = angle_des

        angle = None
        
        if cardinal_angle is not None and diagonal_angle is not None:
            angle = two_angles_average([cardinal_angle, diagonal_angle])
        elif cardinal_angle is not None:
            angle = cardinal_angle
        elif diagonal_angle is not None:
            angle = diagonal_angle

        #print(angle, angle_v, angle_h, angle_asc, angle_des)

        return angle
    
    def detect_rotation(self, image):
        
        # calculate the threshold depending on frames per second
        # 10 degrees per second minimum to detect change
        deg_per_second_thr = 10
        thr = (time() - self.old_time) * deg_per_second_thr
        self.old_time = time()

        # change is 0 if no change, 1 if clockwise, -1 if counterclockwise
        change = 0
        change_amplitude = 0
        angle_result = self.detect_angle(image)

        if self.old_angle_result is not None and angle_result is not None:

            if angle_result > self.old_angle_result + 180:
                diff = angle_result - (self.old_angle_result+360)
            else:
                diff = angle_result - self.old_angle_result
            
            if diff >= thr:
                change = 1
            elif diff <= -thr:
                change = -1
            
            change_amplitude = diff
        
        self.old_angle_result = angle_result
        
        return change, change_amplitude

if __name__ == '__main__':
    md = MarkerDetector()
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()  
        #frame = cv2.imread('images/testaruco2.png')
        #frame = cv2.resize(frame, (640, 480))

        print(md.detect_rotation(frame))

        cv2.imshow('frame', frame)
        sleep(0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()

dictionary = cv2.aruco.DICT_4X4_50


   