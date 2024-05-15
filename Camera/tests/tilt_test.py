import distance
import numpy as np
import matplotlib.pyplot as plt

tilt = np.linspace(-1, 1, 100)

x = np.linspace(-5, 5, 1000)
y = np.linspace(-5, 5, 1000)

xx, yy = np.meshgrid(x, y)
not_tilt = np.sqrt(xx**2 + yy**2)

xx, yy = np.meshgrid(x, y)
tilt = xx + yy

xx, yy = np.meshgrid(x, y)
tilt_2 = -(xx + yy)

print("Not tilt", distance.calculate_tilt(not_tilt))
print("Tilt", distance.calculate_tilt(tilt))
print("Tilt 2", distance.calculate_tilt(tilt_2))

plt.imshow(not_tilt, extent=(x.min(), x.max(), y.min(), y.max()), origin='lower')
plt.show()

plt.imshow(tilt, extent=(x.min(), x.max(), y.min(), y.max()), origin='lower')
plt.show()

plt.imshow(tilt_2, extent=(x.min(), x.max(), y.min(), y.max()), origin='lower')
plt.show()

