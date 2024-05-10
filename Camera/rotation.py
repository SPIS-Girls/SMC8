import numpy as np
import config

class Rotation:

    def __init__(self) -> None:
        self.frame_window = 5
        self.angle_change = None
        self.prev_angles = []
        self.rotation_matrix = self.calculate_rotation_matrix(config.CAMERA_ANGLE)
        self.threshold = 0.15

    def calculate_rotation_matrix(self, angle):
        # Convert the angle to radians
        angle = np.deg2rad(angle)
        # Create the rotation matrix
        return np.array([
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)]
        ])

    def get_angle(self):
        return self.angle_change

    def add_person(self, person):
        person_top_view = self.transform_to_top_view(person[0], 
                                                     person[1], 
                                                     person[2])
        
        current_angle = Rotation.calculate_angle(person_top_view)
        
        if len(self.prev_angles) > self.frame_window:
            prev_angle = self.prev_angles.pop(0)
            diff = np.unwrap([prev_angle - current_angle])[0]

            if diff > self.threshold:
                self.angle_change = 1
            elif diff < -self.threshold:
                self.angle_change = -1
            else:
                self.angle_change = 0
        else:
            self.angle_change = 0

        self.prev_angles.append(current_angle)    

    def transform_to_top_view(self, x, y, z):
        # Create the original 3D point
        point = np.array([x, y, z])
        # Apply the rotation matrix to the point
        rotated_point = np.dot(self.rotation_matrix, point)
        # The x and y coordinates of the rotated point give the top-down view
        top_view_x, top_view_y = rotated_point[0], rotated_point[1]
        return top_view_x, top_view_y

    @staticmethod
    def calculate_angle(person):
        dx = 0.5 - person[0] 
        dy = 0.5 - person[1] 
        return np.arctan2(dx, dy) 