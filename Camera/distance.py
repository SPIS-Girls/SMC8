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

# Check if the region is tilted (smoothly goes from high to low)
# If the region is tilted and smooth, return the angle of the tilt
# If the region is not tilted or not smooth, return 0
def calculate_tilt(depth_frame):
    center_y, center_x = np.array(depth_frame.shape) // 2 # Calculate the center of the depth array
    circ, _ = np.array(depth_frame.shape) // 5 # 20% of depth frame's size
    region = depth_frame[center_y-circ:center_y+circ, center_x-circ:center_x+circ] # Extract a region around the center
    
    # set all the values besides the corners to the mean of the region
    corners = [region[0, 0], region[0, -1], region[-1, 0], region[-1, -1]]
    
    tilt = (np.max(corners) - np.min(corners)) / 1.5
    if np.abs(tilt) < config.TILT_THRESHOLD:
        return 0 

    diff_x = np.diff(np.mean(region, axis=1)) # Calculate the difference in depth values along the x-axis
    diff_y = np.diff(np.mean(region, axis=0)) # Calculate the difference in depth values along the y-axis

    arr_middle_x = np.full(diff_x.shape, diff_x[0])
    arr_middle_y = np.full(diff_y.shape, diff_y[0])

    if not np.isclose(diff_x, arr_middle_x, atol=0.1).all() or not np.isclose(diff_y, arr_middle_y, atol=0.1).all():
        print("Not tilt")
        return 0
    
    ind = np.unravel_index(np.argmin(region, axis=None), region.shape)
    if ind[0] < region.shape[0] // 2:
        tilt = -tilt

    return np.clip(tilt, -1, 1)