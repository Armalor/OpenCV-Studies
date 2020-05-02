import cv2
import os
import numpy as np
import math

width = 800
height = 800

background = np.zeros((width, height, 3)).astype(np.uint8)

background[:] = (55, 75, 55)

# Рисуем оси системы координат (начало координат — в центре экрана)
cv2.line(background, (width//2, 0), (width//2, height), (100, 100, 100), 1)
cv2.line(background, (0, height//2), (width, height//2), (100, 100, 100), 1)


img = np.zeros((width, height, 3)).astype(np.uint8)

thickness = 50


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
