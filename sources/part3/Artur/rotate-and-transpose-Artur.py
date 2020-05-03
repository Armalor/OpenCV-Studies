import cv2
import os
import numpy as np
import math
from matplotlib import pyplot as plt

width = 800
height = 800

background = np.zeros((width, height, 3)).astype(np.uint8)

background[:] = (55, 75, 55)

# Рисуем оси системы координат (начало координат — в центре экрана)
cv2.line(background, (width//2, 0), (width//2, height), (100, 100, 100), 1)
cv2.line(background, (0, height//2), (width, height//2), (100, 100, 100), 1)


img = np.zeros((width, height, 3)).astype(np.uint8)

thickness = 50


def returning(mask):
    mask_left = mask[:width//2,:width//2]
    mask_right = mask[:width//2,width//2:]
    # hsv_left = cv2.cvtColor(mask_left, cv2.COLOR_GRAY2BGR)
    # hsv_left = cv2.cvtColor(hsv_left, cv2.COLOR_BGR2HSV)
    # hsv_right = cv2.cvtColor(mask_right, cv2.COLOR_GRAY2BGR)
    # hsv_right = cv2.cvtColor(hsv_right, cv2.COLOR_BGR2HSV)

    # определить диапазон цветов в HSV (все оттенки, но контраст и насышенность не менее 100)
    hist_left = cv2.calcHist([mask_left], [0], None, [255], [10, 256])
    hist_right = cv2.calcHist([mask_right], [0], None, [255], [10, 256])

    print(max(hist_left))
    print(max(hist_right))

    plt.plot(hist_right, color='red',marker = 'X')
    plt.plot(hist_left, color='yellow', marker='o')

    plt.yscale('log')
    plt.xlim([0, 256])

    plt.show()


def transposition(point: np.array):
    scale = np.array([1,-1])
    trans = np.array([width//2, height//2])
    return point*scale+trans


def rotation(point: np.array, theta_deg):
    theta = math.radians(theta_deg)

    rotate_matrix = np.array([
        [math.cos(theta), math.sin(theta)],
        [-math.sin(theta), math.cos(theta)]
    ])

    ret = rotate_matrix.dot(point)
    return ret.astype(np.int16)


# Собственно, наша «дорога» — трапеция:
figure = [
    (-200, -700),
    (200, -700),
    (25, 300),
    (-25, 300),
]

angle = 0.0
delta = 1.0

while True:

    palette = img.copy()

    for p in range(0, len(figure)):
        start = figure[p]
        finish = figure[(p+1) % len(figure)]

        # Повернули точки на нужный угол
        start = rotation(start, angle)
        finish = rotation(finish, angle)

        # И потом переместили их относительно экранной системы координат:
        start = transposition(start)
        finish = transposition(finish)

        cv2.line(palette, tuple(start), tuple(finish), (255, 255, 254), thickness)

    hsv = cv2.cvtColor(palette, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 1, 1]), np.array([180, 255, 255]))

    # Оставляем те части фона, где нет рисунка:
    res = cv2.bitwise_and(background, background, mask=~mask)
    # Накладываем рисунок на фон:
    res = cv2.bitwise_or(palette, background, mask=None)
    cv2.imshow('res', res)
    cv2.imshow('mask', mask)
    # print(mask)
    key = cv2.waitKey(1)
    # print(key)
    # Вправо:
    if key == ord('a'):
        angle += delta
    # Влево:
    elif key == ord('d'):
        angle -= delta
    # Вниз:
    elif key == ord('w'):
        delta -= 1 if delta > 0 else delta
        # print(delta)
    # Вверх:
    elif key == ord('s'):
        delta += 1
        # print(delta)
    elif key == ord(' '):
           returning(mask)

    if key == 27:
        break