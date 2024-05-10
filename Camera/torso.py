import numpy as np
import config

from one_euro_filter import OneEuroFilter

class Torso:
    def __init__(self) -> None:
        self.prev_torso = None
        self.torso_weigth_effort = []
        self.frame_rate = config.FPS
        self.frame_window = 5
        self.t = 0
        self.one_euro_filter = OneEuroFilter(self.t, 0, min_cutoff=0.004, beta=0.7)

    def get_weigth_effort(self):
        if len(self.torso_weigth_effort) == 0:
            return 0
        
        self.t += 1 
        return self.one_euro_filter(self.t, np.max(self.torso_weigth_effort))
                                    
    def add_torso(self, torso):
        effort = self.calculate_effort(torso)
        self.prev_torso = torso
        self.torso_weigth_effort.append(effort)

        # remove the oldest torso if the list is too long
        if len(self.torso_weigth_effort) > self.frame_window:
            self.torso_weigth_effort.pop(0)

    def calculate_effort(self, new_torso):
        if self.prev_torso is None:
            return 0
        xyz = np.subtract(new_torso, self.prev_torso) * self.frame_rate
        return xyz[0] ** 2 + xyz[1] ** 2 + xyz[2] ** 2
        
            

