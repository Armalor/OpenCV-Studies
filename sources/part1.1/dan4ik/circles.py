import numpy as np
import cv2
import os


def whatcolor(path,tc):
    rgb = cv2.imread(path)
    height, width, depth = rgb.shape
    newWidth = 200
    newHeight = (newWidth * height) // width
    rgb = cv2.resize(rgb, (newWidth, newHeight))

    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)

    lower_g = np.array([36, 70, 70])
    upper_g = np.array([95, 255, 255])

    lower_y = np.array([15, 150, 150])
    upper_y = np.array([35, 255, 255])

    lower_r0 = np.array([0, 150, 150])
    upper_r0 = np.array([15, 255, 255])

    lower_r1 = np.array([160, 150, 150])
    upper_r1 = np.array([180, 255, 255])

    mask = cv2.inRange(hsv, lower_g, upper_g)
    mask = cv2.bitwise_or(mask,cv2.inRange(hsv, lower_y, upper_y))
    mask = cv2.bitwise_or(mask,cv2.inRange(hsv, lower_r0, upper_r0))
    mask = cv2.bitwise_or(mask,cv2.inRange(hsv, lower_r1, upper_r1))


    res = cv2.bitwise_and(rgb, rgb, mask=mask)
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    bilateral_filtered_gray = cv2.bilateralFilter(gray, 5, 175, 175)

    circles = cv2.HoughCircles(bilateral_filtered_gray,cv2.HOUGH_GRADIENT,1,newHeight, param1=150,param2=15,minRadius=0,maxRadius=newHeight//3)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for q in circles[0,:]:
            i = hsv[q[1]][q[0]]
            cv2.circle(res, (i[0], i[1]), i[2], (255, 255, 255), 2)
            if 0 <= i[0] <= 14 or 170 <= i[0] <= 180:
                c = 'red'
            elif 15 <= i[0] <= 35:
                c = 'yellow'
            elif 36 <= i[0] <= 95:
                c = 'green'
            else:
                print(i)
                print(path + " не удалось распознать цвет")
                continue
            print(path + " " + tc + " распознан как " + c + " - " + str(c == tc))
    else:
        print("Круги не найдены")
        hist = cv2.calcHist([hsv], [0], mask, [255], [0, 255])
        i = hist.argmax()
        if 0 <= i <= 14 or 170 <= i <= 180:
            c = 'red'
        if 15 <= i <= 35:
            c = 'yellow'
        if 36 <= i <= 95:
            c = 'green'
        print(path + " " + tc + " распознан как " + c + " - " + str(c == tc))


a = os.listdir('../../../data/traffic-light/red')
b = os.listdir('../../../data/traffic-light/yellow')
c = os.listdir('../../../data/traffic-light/green')

for p in a:
    whatcolor('../../../data/traffic-light/red/' + p, 'red')
for p in b:
    whatcolor('../../../data/traffic-light/yellow/' + p, 'yellow')
for p in c:
    whatcolor('../../../data/traffic-light/green/' + p, 'green')
