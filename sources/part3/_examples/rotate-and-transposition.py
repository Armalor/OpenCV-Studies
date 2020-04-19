import cv2
import os
import numpy as np
import math

width = 800
height = 800

background = np.zeros((width, height, 3)).astype(np.uint8)
background[:] = (55, 75, 55)
cv2.line(background, (width//2, 0), (width//2, height), (255,255,255), 1)
cv2.line(background, (0, height//2), (width, height//2), (255,255,255), 1)


img = np.zeros((width, height, 3)).astype(np.uint8)
#img[:] = (49, 49, 49)
# Start coordinate, here (0, 0)
# represents the top left corner of image
start_point = np.array([0, 0])

# End coordinate, here (250, 250)
# represents the bottom right corner of image
end_point = np.array([15, 300])

color = (255, 0, 0)

# Line thickness of 9 px
thickness = 2


def transposition(point: np.array):

    scale = np.array([1,-1])
    trans = np.array([width//2, height//2])

    return point*scale+trans


def rotation(point: np.array, teta_deg):
    teta = math.radians(teta_deg)


    matrix = np.array([
        [math.cos(teta), math.sin(teta)],
        [-math.sin(teta), math.cos(teta)]
    ])

    ret = matrix.dot(point)
    return ret.astype(np.uint16)


start_point1 = start_point
end_point1 = rotation(end_point, 22.5)

start_point2 = start_point
end_point2 = rotation(end_point, 45)


while True:

    start_point = transposition(start_point)
    start_point1 = transposition(start_point1)
    start_point2 = transposition(start_point2)

    end_point = transposition(end_point)
    end_point1 = transposition(end_point1)
    end_point2 = transposition(end_point2)



    cv2.line(img, tuple(start_point), tuple(end_point), color, thickness)
    cv2.line(img, tuple(start_point1), tuple(end_point1), (0, 255, 0), thickness)
    cv2.line(img, tuple(start_point2), tuple(end_point2), (0, 0, 255), thickness)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([255, 255, 255]))

    res = cv2.bitwise_and(background, background, mask=~mask)
    res = cv2.bitwise_or(img, background, mask=None)

    res1 = cv2.bitwise_and(background,background, mask=None)

    cv2.imshow('res', res)
    cv2.imshow('mask', mask)

    key = cv2.waitKey(1)
    if key == 27:
        break;

cv2.destroyAllWindows()
