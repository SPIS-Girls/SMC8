import mediapipe as mp
import numpy as np
import config

from torso import Torso
from wrist import Wrist
from rotation import Rotation

from mediapipe import solutions
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

PoseLandmarker = mp.tasks.vision.PoseLandmarker

class PoseDetector:
    def __init__(self) -> None:
        self.detector = self.init_detector()
        self.result_video = None
        self.timestamp = 0

        self.torsos = [Torso(), Torso(), Torso(), Torso()]
        self.wrists_left = [Wrist(), Wrist(), Wrist(), Wrist()]
        self.wrists_right = [Wrist(), Wrist(), Wrist(), Wrist()]
        self.rotation = Rotation()


    def __del__(self) -> str:
        pass

    def init_detector(self):
        base_options = python.BaseOptions(model_asset_path='model/pose_landmarker_lite.task')

        options = vision.PoseLandmarkerOptions(
            num_poses=4, # def 1
            min_pose_detection_confidence=0.75, # def 0.5
            min_pose_presence_confidence=0.5, # def 0.5
            min_tracking_confidence=0.15, # def 0.5
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM, # def image
            base_options=base_options,
            output_segmentation_masks=False,
            result_callback=self.process_result)
        d = vision.PoseLandmarker.create_from_options(options)
        
        return d
    
    @staticmethod
    def get_torso_landmarks(landmark):
        return [(landmark[11].x + landmark[12].x + landmark[23].x + landmark[24].x) * 0.25, 
                 (landmark[11].y + landmark[12].y + landmark[23].y + landmark[24].y) * 0.25,
                 (landmark[11].z + landmark[12].z + landmark[23].z + landmark[24].z) * 0.25]
    
    def get_wrist_left_calc(self):
        return [wl.get_yaxis_displacement() for wl in self.wrists_left]
    
    def get_wrist_right_calc(self):
        return [wr.get_yaxis_displacement() for wr in self.wrists_right]
    
    def get_torso_calc(self):
        return [t.get_weigth_effort() for t in self.torsos]
    
    def get_rotation_calc(self):
        return self.rotation.get_angle()

    def process_result(self, result: PoseLandmarker, mp_image : mp.Image, timastamp_ms: int):
        for idx, landmark in enumerate(result.pose_landmarks):
            torso = self.get_torso_landmarks(landmark)
            self.torsos[idx].add_torso(torso)
            self.wrists_left[idx].add_wrist([landmark[15].x, landmark[15].y, landmark[15].z])
            self.wrists_right[idx].add_wrist([landmark[16].x, landmark[16].y, landmark[16].z])

            if idx == 0:
                self.rotation.add_person(torso)

        # add empty values for the rest of the persons
        for i in range(len(result.pose_landmarks), 4):
            self.torsos[i].add_torso([0, 0, 0])
            self.wrists_left[i].add_wrist([0, 0, 0])
            self.wrists_right[i].add_wrist([0, 0, 0])
            if i == 0:
                self.rotation.add_person([0, 0, 0])

        if config.VISUALIZE:
            self.result_video = self.draw_landmarks_on_image(mp_image.numpy_view(), result)
    
    def detect(self, image):
        self.timestamp += 1
        self.detector.detect_async(image, self.timestamp)

        if self.result_video is None:
            return image.numpy_view()
        else:
            return self.result_video
    
    @staticmethod
    def draw_landmarks_on_image(rgb_image, detection_result):
        pose_landmarks_list = detection_result.pose_landmarks
        annotated_image = np.copy(rgb_image)

        # Loop through the detected poses to visualize.
        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]

            # Draw the pose landmarks.
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                solutions.pose.POSE_CONNECTIONS,
                solutions.drawing_styles.get_default_pose_landmarks_style())
        return annotated_image
