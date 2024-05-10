import numpy as np
import cv2

class DepthAnalyzer:
    def __init__(self):
        pass

    def find_heads(self, image):


        print("ra", image[0][0])


        image = (image * 255).astype(np.uint8)

        print(image[0][0])


        cv2.imshow('image', image)

        pass

    def generate_wave(self, image):
        pass

# from depth_analyzer import DepthAnalyzer
# self.da = DepthAnalyzer()
# heads = self.da.find_heads(depth)