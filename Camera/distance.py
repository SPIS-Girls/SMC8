import numpy as np
import cv2
import config
from one_euro_filter import OneEuroFilter 

class Distance:
    def __init__(self):
        self.t = 0
        self.euro_filt_distance = OneEuroFilter(self.t, 0, min_cutoff=0.004, beta=0.7)
        self.euro_filt_tilt = OneEuroFilter(self.t, 0, min_cutoff=0.004, beta=0.7)
        self.depth_frame = None
        self.prev_frame = None

    # Get the intrinsic matrix from the coefficients
    # example usage: intrinsic_mat = get_intrinsic_mat_from_coeffs(session.get_intrinsic_mat())
    @staticmethod
    def get_intrinsic_mat_from_coeffs(coeffs):
        return np.array([[coeffs.fx,         0, coeffs.tx],
                            [        0, coeffs.fy, coeffs.ty],
                            [        0,         0,         1]])
    
    def push_depth_frame(self, depth_frame):
        self.prev_frame = self.depth_frame
        self.depth_frame = depth_frame

    def get_parameters(self) -> tuple: 
        self.t += 1
        return self.euro_filt_distance(self.t, self.calculate_depth_middle()), self.euro_filt_tilt(self.t, self.calculate_tilt())
    
    def is_on_the_floor(self):
        center_y, center_x = np.array(self.depth_frame.shape) // 2 # Calculate the center of the depth array
        area = int(0.1 * center_y) # Calculate 10% of the center
        if self.depth_frame[center_y, center_x] > config.ROOM_HEIGHT:
            # check if central 20% size square is flat
            region = self.depth_frame[center_y-area:center_y+area, center_x-area:center_x+area] # Extract the 20% region around the center
            # check if the region is flat, if all values are close to the center value
            arr_middle = np.full(region.shape, self.depth_frame[center_y, center_x])
            return np.isclose(region, arr_middle, atol=0.05).all()

    # Calculate the depth of the middle of the depth frame
    def calculate_depth_middle(self):
        center_y, center_x = np.array(self.depth_frame.shape) // 2 # Calculate the center of the depth array
        region = self.depth_frame[center_y-2:center_y+2, center_x-2:center_x+2] # Extract the 4x4 region around the center
        return np.mean(region) # Calculate the mean of the region

    def calculate_crunchiness(self):
        if self.prev_frame is None or self.depth_frame is None:
            return 0
        
        return np.mean(np.abs(self.prev_frame - self.depth_frame))

    # Check if the region is tilted (smoothly goes from high to low)
    # If the region is tilted and smooth, return the angle of the tilt
    # If the region is not tilted or not smooth, return 0
    def calculate_tilt(self):
        crunchiness = self.calculate_crunchiness()
        print("Crunchiness: ", crunchiness)
        if crunchiness > config.CRUNCHINESS_THRESHOLD_LOW:
            # print("Too much crunchiness", crunchiness)
            return 0

        center_y, center_x = np.array(self.depth_frame.shape) // 2 # Calculate the center of the depth array
        circ, _ = np.array(self.depth_frame.shape) // 5 # 20% of depth frame's size
        region = self.depth_frame[center_y-circ:center_y+circ, center_x-circ:center_x+circ] # Extract a region around the center
        
        # set all the values besides the corners to the mean of the region
        corners = [region[0, 0], region[0, -1], region[-1, 0], region[-1, -1]]
        
        tilt = (np.max(corners) - np.min(corners)) / 1.5
        if np.abs(tilt) < config.TILT_THRESHOLD:
            # print("Not enough tilt", tilt)
            return 0 
        
        ind = np.unravel_index(np.argmin(region, axis=None), region.shape)
        if ind[0] < region.shape[0] // 2:
            tilt = -tilt

        print("Tilt: ", tilt)

        return np.clip(tilt, -1, 1)