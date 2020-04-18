import cv2
import os
import numpy as np
import math


background = np.zeros((800, 800)).astype(np.uint8)
background[:] = 50

img = np.zeros((800, 800)).astype(np.uint8)

# Start coordinate, here (0, 0)
# represents the top left corner of image
start_point = np.array([0, 0])

# End coordinate, here (250, 250)
# represents the bottom right corner of image
end_point = np.array([0, 500])

color = 255

# Line thickness of 9 px
thickness = 3



mask = cv2.inRange(img, np.array([255]), np.array([255]))


def rotation(point: np.array, teta):
    rad = math.radians(teta)
    print(point, rad)

    matrix = np.array([
        [math.cos(rad), math.sin(rad)],
        [-math.sin(rad), math.cos(rad)]
    ])

    x1 = point[0] * np.cos(rad) + point[1] * np.sin(rad)
    y1 = point[1] * np.cos(rad) - point[0] * np.sin(rad)

    ret = np.array([x1, y1]).astype(np.uint8)
    print('direct:', ret)

    ret = matrix.dot(point)
    print('matrix:', ret.astype(np.uint8))

    return ret.astype(np.uint8)


start_point1 = start_point
end_point1 = rotation(end_point, 45)

start_point2 = start_point
end_point2 = rotation(end_point, 90)


while True:


    img = cv2.line(img, tuple(start_point), tuple(end_point), color, thickness)
    img = cv2.line(img, tuple(start_point1), tuple(end_point1), 200, thickness)
    img = cv2.line(img, tuple(start_point2), tuple(end_point2), 100, thickness)

    res = cv2.bitwise_or(img, background, mask=None)
    cv2.imshow('img', res)

    key = cv2.waitKey(1)
    if key == 27:
        break;

cv2.destroyAllWindows()
