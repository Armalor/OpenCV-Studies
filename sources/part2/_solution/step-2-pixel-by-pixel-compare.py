import cv2
import imutils
import numpy as np
import os

signsFiles = [
    '../../../data/road-signs/approaching-a-pedestrian-crossing.jpg',
    '../../../data/road-signs/footpath.jpg',
    '../../../data/road-signs/left-turn.jpg',
    '../../../data/road-signs/no-overtaking.jpg',
    '../../../data/road-signs/movement-prohibition.jpg',
]

signs = {}

for i in range(len(signsFiles)):
    file = signsFiles[i]

    filename = os.path.basename(file)
    filename = os.path.splitext(filename)[0]

    sign = cv2.imread(file)
    sign = imutils.resize(sign, width=128, height=128)

    hsv = cv2.cvtColor(sign, cv2.COLOR_BGR2HSV)

    mask_blue = cv2.inRange(hsv, np.array([98, 50, 100]), np.array([108, 255, 255]))
    mask_black = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([255, 10, 10]))
    # определить диапазон и маску красного цвета в HSV (красный цвет с обоих концов, поэтому маски красного - две)
    mask_r0 = cv2.inRange(hsv, np.array([0, 150, 150]), np.array([14, 255, 255]))
    mask_r1 = cv2.inRange(hsv, np.array([160, 150, 150]), np.array([180, 255, 255]))

    s_mask = cv2.bitwise_or(mask_r0, mask_r1)
    s_mask = cv2.bitwise_or(s_mask, mask_black)
    s_mask = cv2.bitwise_or(s_mask, mask_blue)

    signs[filename] = s_mask

    cv2.imshow(str(i), signs[filename])



ranges = {
    'min_h1': [98, 180],
    'max_h1': [108, 180],

    'min_h2': [148, 180],
    'max_h2': [180, 180],

    'min_s':  [30, 255],
    'max_s':  [255, 255],

    'min_v':  [39, 255],
    'max_v':  [255, 255],
}


def setHandlerToTrackbar(name):
    def handler(x):
        global ranges
        ranges[name][0] = x
        print(*[(x, ranges[x][0]) for x in ranges if ranges[x][0] != ranges[x][1]])
    return handler


cap = cv2.VideoCapture(0)

cv2.namedWindow('result')

for name, value in ranges.items():
    cv2.createTrackbar(name, 'result', 0, ranges[name][1], setHandlerToTrackbar(name))
    cv2.setTrackbarPos(name, 'result', value[0])


roImgExists = False
def onMouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP and roImgExists == True:
        print(roImg.shape)
        for name, img in signs.items():
            commonPix = 0




cv2.setMouseCallback('result', onMouse)

while True:
    roImgExists = False
    ret, frame = cap.read()
    frameCopy = frame.copy()

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Размываем HSV-картинку с матрицей размытия 5*5
    frame_hsv = cv2.blur(frame_hsv, (3,3))

    mask1 = cv2.inRange(frame_hsv, (ranges['min_h1'][0], ranges['min_s'][0], ranges['min_v'][0]), (ranges['max_h1'][0], ranges['max_s'][0], ranges['max_v'][0]))
    mask2 = cv2.inRange(frame_hsv, (ranges['min_h2'][0], ranges['min_s'][0], ranges['min_v'][0]), (ranges['max_h2'][0], ranges['max_s'][0], ranges['max_v'][0]))
    mask = cv2.bitwise_or(mask1, mask2)

    # Избавляемся от мелких объектов.
    # Уменньшаем контуры белых объектов: если в рамках матрицы есть "не белый" пиксель, то все становится черным.
    matrix = (30,30)
    mask = cv2.erode(mask, matrix, iterations=2)
    # Обратная функции erode: если есть белый пиксель, весь контур становится белым.
    mask = cv2.dilate(mask, matrix, iterations=4)
    # Избавились.

    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Ищем контуры
    contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # Сами структуры контуров хранятся в начальном элементе возвращаемого значения:
    contours = contours[0]

    # Их, кстати, может и не быть:
    if contours:
        # Сортируем по убыванию площади контура — хотим один самый большой:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # Третий аргумент — это индекс контура, который мы хотим вывести. Мы хотим самый большой.
        # Вывести все можно, передав -1 вместо 0:
        #cv2.drawContours(result, contours, 0, (255, 0, 0), 1)

        # Получаем прямоугольник, обрамляющий наш контур:
        (x, y, w, h) = cv2.boundingRect(contours[0])

        # И выводим его:
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 1)


        # Аналогично строим минимальную описанную вокруг наибольшего контура окружность:
        (x1, y1), radius = cv2.minEnclosingCircle(contours[0])
        center = (int(x1), int(y1))
        radius = int(radius)
        cv2.circle(result, center, radius, (0, 255, 0), 1)

        #Получаем детектируемый знак в виде region of interests:
        roImg = frameCopy[y:y+h, x:x+w]
        roImg = imutils.resize(roImg, width=128, height=128)
        cv2.imshow('roImg', roImg)
        roImgExists = True



    cv2.imshow('maskDi', mask)
    cv2.imshow('result', result)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()