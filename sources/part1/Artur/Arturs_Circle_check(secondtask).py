import cv2
from matplotlib import pyplot as plt
import os
import numpy as np
import time
import imutils

ext = 'jpg'
dirs = ['/green/', '/red/', '/yellow/']
path = '../../../data/traffic-light'


def test_hist(filename):
    rgb = cv2.imread(filename)
    height, width, depth = rgb.shape
    newWidth = 200
    newHeight = (newWidth * height) // width

    rgb = imutils.resize(rgb, width=newWidth)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)

    # определить диапазон и маску зеленого цвета в HSV
    lower_g = np.array([36, 50, 100])
    upper_g = np.array([95, 255, 255])
    mask_g = cv2.inRange(hsv, lower_g, upper_g)

    # определить диапазон и маску желтого цвета в HSV
    lower_y = np.array([15, 100, 100])
    upper_y = np.array([35, 255, 255])
    mask_y = cv2.inRange(hsv, lower_y, upper_y)

    # определить диапазон и маску красного цвета в HSV (красный цвет с обоих концов, поэтому маски красного - две)
    lower_r0 = np.array([0, 150, 150])
    upper_r0 = np.array([14, 255, 255])
    mask_r0 = cv2.inRange(hsv, lower_r0, upper_r0)

    lower_r1 = np.array([160, 150, 150])
    upper_r1 = np.array([180, 255, 255])
    mask_r1 = cv2.inRange(hsv, lower_r1, upper_r1)

    mask = cv2.bitwise_or(mask_r0, mask_r1)
    mask = cv2.bitwise_or(mask, mask_y)
    mask = cv2.bitwise_or(mask, mask_g)

    # Побитовая-И-маска и исходное изображение
    res = cv2.bitwise_and(rgb, rgb, mask=mask)
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    bilateral_filtered_gray = cv2.bilateralFilter(gray, 5, 175, 175)

    circles = cv2.HoughCircles(bilateral_filtered_gray, cv2.HOUGH_GRADIENT, 1, newHeight, param1=150, param2=15,
                               minRadius=0, maxRadius=newHeight // 3)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(res, (i[0], i[1]), i[2], (255, 255, 255), 2)

    hist = cv2.calcHist([hsv], [0], mask, [180], [0, 180])
    plt.plot(hist, color='gray')
    plt.xlim([0, 180])
    plt.ylim([0, 2000])
    plt.show()
    return hist,rgb, mask,bilateral_filtered_gray, res


def getMainColor(hist: bytearray) -> tuple:
    point = np.argmax(hist)
    color = None

    if point >= 0 and point <= 14 or point > 160:
        color = 'red'
    elif point >= 15 and point < 35:
        color = 'yellow'
    elif point >= 36 and point <= 95:
        color = 'green'

    return color, point

sp = []
for d in dirs:
    for f in os.listdir(path + d):
        if f.endswith(ext):
            sp.append(path+d+f)
i = int(input("Просьба начинать отсчет с нуля)"))
hist,rgb,mask,bilateral_filtered_gray,res = test_hist(sp[i])
print(getMainColor(hist))

cv2.imshow('img', rgb)
cv2.imshow('mask', mask)
cv2.imshow('gray', bilateral_filtered_gray)
cv2.imshow('res', res)

while 1:
    if cv2.waitKey(1) == 27:
        break


cv2.destroyAllWindows()