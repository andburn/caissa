import sys

import cv2 as cv
import numpy as np


# get the input file and convert to grayscale
img_file = sys.argv[1]
img = cv.imread(img_file)
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

edges = cv.Canny(gray, 100, 200)
cv.imwrite('captures/_canny.jpg', edges)

# detect lines using canny edges
lines = cv.HoughLines(edges, 1, np.pi/180, 180)

for line in lines:
    rho,theta = line[0]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))
    cv.line(img, (x1,y1), (x2,y2), (0,0,255), 2)

cv.imwrite('captures/_lines.jpg', img)

# use Harris/Shi-Tomasi corner detector on original grayscale image
corners = cv.goodFeaturesToTrack(gray, 100, 0.04, 8)

for i in corners:
    x, y = i.ravel()
    cv.circle(gray, (x,y), 3, 255, -1)

cv.imwrite('captures/_corners.jpg', gray)
