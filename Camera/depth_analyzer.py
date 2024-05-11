import numpy as np
import cv2
import math
import random

class DepthAnalyzer:
    def __init__(self):
        pass

    def generate_wave(self, depth, max_depth):
        depth = 255.0 * (1.0 - depth / max_depth) # scale depth by max_depth and invert colors
        cv2.imwrite('aaaa' + str(random.randint(0, 1000)) + ".png", depth)

        cv2.imshow('Depth', depth)

        print("ra", depth[0][0])

        depth = (depth * 255).astype(np.uint8)


        print(depth[0][0])
        pass

# from depth_analyzer import DepthAnalyzer
# self.da = DepthAnalyzer()
# heads = self.da.find_heads(depth, max_depth)

if __name__ == '__main__':
    da = DepthAnalyzer()
    while True:
        depth = cv2.imread("TEMP/aaaa802.png", cv2.IMREAD_GRAYSCALE)
        heads = da.generate_wave(depth, 5)
        