import sys

import cv2 as cv
import numpy as np


# mouse click globals
points = []
output_size = 300
output_dims = np.float32([
    [0,0],
    [output_size, 0],
    [0, output_size],
    [output_size, output_size]
    ])


# mouse click callback function
def mouse_click(event, x, y, flags, param):
    global ui_img

    if event == cv.EVENT_LBUTTONDOWN:
        cv.circle(ui_img, (x,y), 5, (255,0,0), -1)
        points.append([x,y])


def get_distance(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2


def find_nearest(points, p):
    nearest = [0, 0]
    ndist = -1
    for pt in points:
        dist = get_distance(p, pt[0])
        if ndist < 0 or dist < ndist:
            ndist = dist
            nearest = pt
    return nearest


# based on manual corners transform perspective
def adjust_image(img, mask, points, size):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # use Harris/Shi-Tomasi corner detector on image
    corners = cv.goodFeaturesToTrack(gray, 85, 0.04, 8, mask=mask)

    # transform perspective
    corner_points = []
    for p in points:
        corner_points.append(find_nearest(corners, p))

    # show corners
    for i in corners:
        x, y = i.ravel()
        cv.circle(gray, (x,y), 3, 255, -1)
        for c in corner_points:
            if x == c[0][0] and y == c[0][1]:
                cv.circle(gray, (x,y), 3, 0, -1)
    cv.imwrite('captures/_corners.jpg', gray)

    corner_points = np.float32(corner_points)
    transform = cv.getPerspectiveTransform(corner_points, output_dims)
    output = cv.warpPerspective(img, transform, (output_size, output_size))
    cv.imwrite('captures/_perspective.jpg', output)


# read the captured image from file
img_file = sys.argv[1]
img = cv.imread(img_file)
# crop out the known upper area of image
img = img[210:]
# read board mask image
mask = cv.imread('captures/board_mask.jpg', cv.IMREAD_GRAYSCALE)

# show window
cv.namedWindow('image')
cv.setMouseCallback('image', mouse_click)

ui_img = img.copy()
# ui loop
while(1):
    cv.imshow('image', ui_img)
    # close window on ESC
    if cv.waitKey(20) & 0xFF == 27:
        adjust_image(img, mask, points, output_size)
        break

cv.destroyAllWindows()
