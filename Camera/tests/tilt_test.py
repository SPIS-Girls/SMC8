import distance
import numpy as np
import matplotlib.pyplot as plt

tilt = np.linspace(-1, 1, 100)

x = np.linspace(0, 0.2, 1000)
y = np.linspace(0, 0.9, 1000)

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

print("Not tilt", distance.calculate_tilt(not_tilt))
print("Tilt", distance.calculate_tilt(tilt))
print("Tilt 2", distance.calculate_tilt(tilt_2))
print("Tilt 3", distance.calculate_tilt(tilt_3))
print("Tilt 4", distance.calculate_tilt(tilt_4))


