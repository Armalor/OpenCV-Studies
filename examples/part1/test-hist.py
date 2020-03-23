import cv2
from matplotlib import pyplot as plt
import numpy as np

rgb_r = cv2.imread('../../data/traffic-light/red/light-0-red.jpg')
rgb_y = cv2.imread('../../data/traffic-light/yellow/light-0-yellow.jpg')
rgb_g = cv2.imread('../../data/traffic-light/green/light-0-green.jpg')

height, width, depth = rgb_r.shape
newWidth = 200
newHeight = (newWidth * height) // width
rgb_r = cv2.resize(rgb_r, (newWidth, newHeight))

height, width, depth = rgb_y.shape
newWidth = 200
newHeight = (newWidth * height) // width
rgb_y = cv2.resize(rgb_y, (newWidth, newHeight))

height, width, depth = rgb_g.shape
newWidth = 200
newHeight = (newWidth * height) // width
rgb_g = cv2.resize(rgb_g, (newWidth, newHeight))

hsv_r = cv2.cvtColor(rgb_r, cv2.COLOR_BGR2HSV)
hsv_y = cv2.cvtColor(rgb_y, cv2.COLOR_BGR2HSV)
hsv_g = cv2.cvtColor(rgb_g, cv2.COLOR_BGR2HSV)




# определить диапазон цветов в HSV (все оттенки, но контраст и насышенность не менее 100)
lower = np.array([0, 100, 100])
upper = np.array([180, 255, 255])
mask = cv2.inRange(hsv_g, lower, upper)

hist_g = cv2.calcHist([hsv_g], [0], mask, [180], [0, 180])

mask = cv2.inRange(hsv_r, lower, upper)
hist_r = cv2.calcHist([hsv_r], [0], mask, [180], [0, 180])

plt.plot(hist_r, color='red')

mask = cv2.inRange(hsv_y, lower, upper)
hist_y = cv2.calcHist([hsv_y], [0], mask, [180], [0, 180])

plt.plot(hist_y, color='yellow')

plt.plot(hist_g, color='green')
plt.xlim([0, 180])
plt.ylim([0, 4000])


plt.show()