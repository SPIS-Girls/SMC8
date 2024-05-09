import numpy as np
import config

from one_euro_filter import OneEuroFilter

class Wrist:
    def __init__(self) -> None:
        self.wrist = []
        self.frame_rate = config.FPS
        self.frame_window = 5
        self.t = 0
        self.one_euro_filter = OneEuroFilter(self.t, 0, min_cutoff=0.004, beta=0.7)

    def add_wrist(self, wrist):
        self.wrist.append(wrist)

        # remove the oldest wrist if the list is too long
        if len(self.wrist) > self.frame_window:
            self.wrist.pop(0)

    def get_zaxis_displacement(self):
        if len(self.wrist) == 0:
            return 0
        
        self.t += 1 
        return self.one_euro_filter(self.t, self.wrist[-1][2] - self.wrist[0][2])

        
            

