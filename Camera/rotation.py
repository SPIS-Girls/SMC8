import numpy as np

class Rotation:

    def __init__(self) -> None:
        self.angle_change = None
        self.prev_angle = 0

    def get_angle(self):
        return self.angle_change

    def add_person(self, person):
        current_angle = Rotation.calculate_angle(person)
        self.angle_change = current_angle - self.prev_angle
        self.prev_angle = current_angle

    @staticmethod
    def calculate_angle(person):
        dx = 0.5 - person[0] 
        dy = 0.5 - person[1] 
        return np.arctan2(dx, dy) 