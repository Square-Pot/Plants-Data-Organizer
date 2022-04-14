import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

img = cv.imread(r"/home/dntx/win/reps/DataMatrix-Sorter/app/l1.jpg")

# Initiate ORB detector
orb = cv.ORB_create()

# find the keypoints with ORB
kp = orb.detect(img,None)

# compute the descriptors with ORB
kp, des = orb.compute(img, kp)

# draw only keypoints location,not size and orientation
img2 = cv.drawKeypoints(img, kp, None, color=(0,255,0), flags=0)

plt.imshow(img2), plt.show()