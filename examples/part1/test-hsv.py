import cv2
from matplotlib import pyplot as plt
import numpy as np

green = np.uint8 ([[[0,255,0]]])
hsv_green = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
print ('green', hsv_green, sep=': ')

yellow = np.uint8 ([[[128  , 128, 0]]])
hsv_yellow = cv2.cvtColor(yellow, cv2.COLOR_BGR2HSV)
print ('yellow', hsv_yellow, sep=': ')

red = np.uint8 ([[[255 , 0, 0], [1, 0, 0]]])
hsv_red = cv2.cvtColor(red, cv2.COLOR_BGR2HSV)
print ('red', hsv_red, sep=': ')

rgb = cv2.imread('../../data/traffic-light/green/light-3-green.jpg')

height, width, depth = rgb.shape
newWidth = 200
newHeight = (newWidth * height) // width

rgb = cv2.resize(rgb, (newWidth, newHeight))
hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)

# определить диапазон и маску зеленого цвета в HSV
lower_g = np.array([36, 100, 100])
upper_g = np.array([75, 255, 255])
mask_g = cv2.inRange(hsv, lower_g, upper_g)

# определить диапазон и маску желтого цвета в HSV
lower_y = np.array([15, 150, 150])
upper_y = np.array([35, 255, 255])
mask_y = cv2.inRange(hsv, lower_y, upper_y)

# определить диапазон и маску красного цвета в HSV (красный цвет с обоих концов, поэтому маски красного - две)
lower_r0 = np.array([0, 100, 100])
upper_r0 = np.array([15, 255, 255])
mask_r0 = cv2.inRange(hsv, lower_r0, upper_r0)

lower_r1 = np.array([160, 100, 100])
upper_r1 = np.array([180, 255, 255])
mask_r1 = cv2.inRange(hsv, lower_r1, upper_r1)

mask = cv2.bitwise_or(mask_r0, mask_r1)
mask = cv2.bitwise_or(mask, mask_y)
mask = cv2.bitwise_or(mask, mask_g)



# Побитовая-И-маска и исходное изображение
res = cv2.bitwise_and(rgb, rgb, mask=mask)


cv2.imshow('img', rgb)
cv2.imshow('mask', mask)
cv2.imshow('res', res)

while 1:
    if cv2.waitKey(1) == 27:
        break


cv2.destroyAllWindows()