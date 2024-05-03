import mediapipe as mp
import numpy as np

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

    def __del__(self) -> str:
        pass

    def init_detector(self):
        base_options = python.BaseOptions(model_asset_path='model/pose_landmarker_lite.task')
        # running mode default is image (which makes sense for us)
        options = vision.PoseLandmarkerOptions(
            num_poses=4, # def 1
            min_pose_detection_confidence=0.22, # def 0.5
            min_pose_presence_confidence=0.5, # def 0.5
            min_tracking_confidence=0.5, # def 0.5
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            base_options=base_options,
            output_segmentation_masks=False,
            result_callback=self.process_result)
        d = vision.PoseLandmarker.create_from_options(options)
        
        return d
    
    @staticmethod
    def get_torso_landmarks(landmarks: PoseLandmarker):
        return [[(landmark[11].x + landmark[12].x + landmark[23].x + landmark[24].x) * 0.25, 
                 (landmark[11].y + landmark[12].y + landmark[23].y + landmark[24].y) * 0.25,
                 (landmark[11].z + landmark[12].z + landmark[23].z + landmark[24].z) * 0.25]
                 for landmark in landmarks] 
    
    def process_result(self, result: PoseLandmarker, mp_image : mp.Image, timastamp_ms: int):
        wrists_left = [[landmark[15].x, landmark[15].y, landmark[15].z] for landmark in result.pose_landmarks]
        wrists_right = [[landmark[16].x, landmark[16].y, landmark[16].z] for landmark in result.pose_landmarks]
            # TODO mean across shoulders and hips (11, 12, 23, 24)
        torsos = self.get_torso_landmarks(result.pose_landmarks) 
        print("People count:", len(result.pose_landmarks))
        print("wrists_L", wrists_left)
        print("wrists_R", wrists_right)
        print("torsos", torsos)

        # TODO CHECK IF THIS WORKS
        # self.client.send_message("/wrists_L", wrists_left)
        # self.client.send_message("/wrists_R", wrists_right)
        # self.client.send_message("/torsos", torsos)
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
