import mediapipe as mp
import numpy as np

from mediapipe import solutions
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2


class PoseDetector:
    def __init__(self) -> None:
        self.detector = self.init_detector()

    def __del__(self) -> str:
        pass

    def init_detector(self):
        base_options = python.BaseOptions(model_asset_path='model/pose_landmarker_full.task')
        # running mode default is image (which makes sense for us)
        options = vision.PoseLandmarkerOptions(
            num_poses=4, # def 1
            min_pose_detection_confidence=0.22, # def 0.5
            min_pose_presence_confidence=0.5, # def 0.5
            min_tracking_confidence=0.5, # def 0.5
            base_options=base_options,
            output_segmentation_masks=True)
        d = vision.PoseLandmarker.create_from_options(options)
        
        return d
    
    def detect(self, image):
        return self.detector.detect(image)
    
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
