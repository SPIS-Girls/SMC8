import numpy as np
import config

# Get the intrinsic matrix from the coefficients
# example usage: intrinsic_mat = get_intrinsic_mat_from_coeffs(session.get_intrinsic_mat())
def get_intrinsic_mat_from_coeffs(coeffs):
    return np.array([[coeffs.fx,         0, coeffs.tx],
                        [        0, coeffs.fy, coeffs.ty],
                        [        0,         0,         1]])

# Calculate the depth of the middle of the depth frame
def calculate_depth_middle(depth_frame):
    center_y, center_x = np.array(depth_frame.shape) // 2 # Calculate the center of the depth array
    region = depth_frame[center_y-2:center_y+2, center_x-2:center_x+2] # Extract the 4x4 region around the center
    return np.mean(region) # Calculate the mean of the region

def is_on_the_floor(depth_frame):
    center_y, center_x = np.array(depth_frame.shape) // 2 # Calculate the center of the depth array
    area = int(0.1 * center_y) # Calculate 10% of the center
    if depth_frame[center_y, center_x] > config.ROOM_HEIGHT:
        # check if central 20% size square is flat
        region = depth_frame[center_y-area:center_y+area, center_x-area:center_x+area] # Extract the 20% region around the center
        # check if the region is flat, if all values are close to the center value
        arr_middle = np.full(region.shape, depth_frame[center_y, center_x])
        return np.isclose(region, arr_middle, atol=0.05).all()
