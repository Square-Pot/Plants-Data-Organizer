# https://stackoverflow.com/questions/69961871/how-to-compute-mean-and-standard-deviation-of-edges-canny-edge-detection-in-ope
# https://answers.opencv.org/question/119161/detecting-not-decoding-datamatrix-rectangle-regions-in-an-image/

from re import M
import cv2
import numpy as np

image = cv2.imread(r"/home/dntx/win/reps/DataMatrix-Sorter/app/IMG_20220330_0757191_50p.jpg")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.medianBlur(gray, 5)


mean, std = cv2.meanStdDev(blur)

print(mean, std)

x = 1.7

tr_1 = mean - x*std
tr_2 = mean + x*std


# threshold on background color
thresh = cv2.inRange(blur, tr_1, tr_2)


# sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
# sharpen = cv2.filter2D(blur, -1, sharpen_kernel)

# thresh = cv2.threshold(sharpen,220,255, cv2.THRESH_BINARY_INV)[1]
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
# close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)


# mser = cv2.MSER_create()
# mser.setMinArea(50)
# mser.setMaxArea(100)
# regions, _ = mser.detectRegions(close)

# hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
# cv2.polylines(image, hulls, 1, (0, 0, 255), 2)




# cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = cnts[0] if len(cnts) == 2 else cnts[1]

# print(cnts)

# min_area = 100
# max_area = 2500
# image_number = 0
# for c in cnts:
#     area = cv2.contourArea(c)
#     print(area)
#     if area > min_area and area < max_area:
#         x,y,w,h = cv2.boundingRect(c)
#         # ROI = image[y:y+h, x:x+w]
#         # cv2.imwrite('ROI_{}.png'.format(image_number), ROI)
#         cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)
        # image_number += 1

# cv2.imshow('gray', gray)
# cv2.imshow('blur', blur)
# cv2.imshow('sharpen', sharpen)
cv2.imshow('thresh', thresh)
cv2.waitKey()