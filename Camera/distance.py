import numpy as np

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