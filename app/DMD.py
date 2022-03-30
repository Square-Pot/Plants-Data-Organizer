import cv2 as cv
import numpy as np
import sys

img = cv.imread(r"/home/dntx/win/reps/DataMatrix-Sorter/app/IMG_20220330_0757191_50p.jpg")

if img is None:
    sys.exit("COuld not read the image.")



gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

vis = img.copy()

# blur = cv.blur(gray, (5, 5))
ret, thresh = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)


mser = cv.MSER_create()
# mser.setMinArea(300)
# mser.setMaxArea(4000)
regions, _ = mser.detectRegions(thresh)

# regs = []
# for r in regions:
#     try:
#         regs.append(r.reshape(-1, 1, 2))
#     except Exception as e:
#         print(e)

# print(len(regs))

# hulls = [cv.convexHull(regs)]

hulls = [cv.convexHull(p.reshape(-1, 1, 2)) for p in regions]
cv.polylines(vis, hulls, 1, (0, 0, 255), 2)





# # # rect top-left and bottom right corner
# # cv.rectangle(img, (384,0), (510,128), (0,255,0), 3)

# print(im)



cv.imshow("Display window", vis)
k = cv.waitKey(0)

# if k == ord("s"):
#     cv.imwrite("IMG_20220330_0757191.png", img)






class DMD:
    """
    |   Data Matrix detector and decoder
    """


    pass