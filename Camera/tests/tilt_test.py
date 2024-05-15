import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import distance
import numpy as np
import matplotlib.pyplot as plt

tilt = np.linspace(-1, 1, 100)

x = np.linspace(0, 1, 100)
y = np.linspace(0, 1, 100)

xx, yy = np.meshgrid(x, y)
not_tilt = np.sqrt(xx**2 + yy**2)

xx, yy = np.meshgrid(x, y)
tilt = xx + yy

xx, yy = np.meshgrid(x, y)
tilt_2 = -(xx + yy)

xx, yy = np.meshgrid(x, y)
tilt_3 = (xx - yy)

xx, yy = np.meshgrid(x, y)
tilt_4 = -(xx - yy)

print("Not tilt:", distance.calculate_tilt(not_tilt))
print("Tilt:", distance.calculate_tilt(tilt))
print("Tilt 2:", distance.calculate_tilt(tilt_2))
print("Tilt 3:", distance.calculate_tilt(tilt_3))
print("Tilt 4:", distance.calculate_tilt(tilt_4))


# Add noise
noise = np.random.normal(0, 0.09, (100, 100)) # 0.5 is the threshold where we still get tilt

tilt = tilt + noise
tilt_2 = tilt_2 + noise
tilt_3 = tilt_3 + noise
tilt_4 = tilt_4 + noise
print("Tilt + Noise:", distance.calculate_tilt(tilt))
print("Tilt 2 + Noise:", distance.calculate_tilt(tilt_2))
print("Tilt 3 + Noise:", distance.calculate_tilt(tilt_3))
print("Tilt 4 + Noise:", distance.calculate_tilt(tilt_4))

# plt.imshow(tilt)
# plt.show()

# read image from aaaa30.png
depth_frame = plt.imread("../images/aaaa30.png")

print("Image", distance.calculate_tilt(np.rot90(depth_frame * 3, k=1)))
