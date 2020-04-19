import cv2
import os
import numpy as np
import math

width = 800
height = 800

background = np.zeros((width, height, 3)).astype(np.uint8)
background[:] = (55, 75, 55)
cv2.line(background, (width//2, 0), (width//2, height), (100, 100, 100), 1)
cv2.line(background, (0, height//2), (width, height//2), (100, 100, 100), 1)


img = np.zeros((width, height, 3)).astype(np.uint8)
#img[:] = (49, 49, 49)
# Start coordinate, here (0, 0)
# represents the top left corner of image
start_point = np.array([0, 0])

# End coordinate, here (250, 250)
# represents the bottom right corner of image
end_point = np.array([15, 300])

color = (254, 254, 254)

# Line thickness of 9 px
thickness = 5


def transposition(point: np.array):

    scale = np.array([1,-1])
    trans = np.array([width//2, height//2])

    return point*scale+trans


def rotation(point: np.array, theta_deg):

    theta = math.radians(theta_deg)

    matrix = np.array([
        [math.cos(theta), math.sin(theta)],
        [-math.sin(theta), math.cos(theta)]
    ])

    ret = matrix.dot(point)
    return ret.astype(np.int16)


figure = [
    (-200, -700),
    (200, -700),
    (25, 300),
    (-25, 300),
]

angle = 0.0
delta = 1.0

while True:

    pallete = img.copy()

    for p in range(0, len(figure)):
        start = figure[p]
        finish = figure[(p+1) % len(figure)]

        start = rotation(start, angle)
        finish = rotation(finish, angle)

        start = transposition(start)
        finish = transposition(finish)

        cv2.line(pallete, tuple(start), tuple(finish), (255, 255, 254), thickness)

    hsv = cv2.cvtColor(pallete, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 1, 1]), np.array([180, 255, 255]))

    res = cv2.bitwise_and(background, background, mask=~mask)
    res = cv2.bitwise_or(pallete, background, mask=None)

    res1 = cv2.bitwise_and(background,background, mask=None)

    cv2.imshow('res', res)
    cv2.imshow('mask', mask)

    key = cv2.waitKeyEx(1)

    # Вправо:
    if key == 2555904:
        angle += delta
    # Влево:
    elif key == 2424832:
        angle -= delta
    # Вниз:
    elif key == 2621440:
        delta -= 1 if delta > 0 else delta
        print(delta)
    # Вверх:
    elif key == 2490368:
        delta += 1
        print(delta)

    if key == 27:
        break

cv2.destroyAllWindows()
