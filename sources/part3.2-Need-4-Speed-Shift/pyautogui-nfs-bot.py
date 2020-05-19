import pyautogui
import time
import numpy as np
import cv2
import imutils
import classes.keyboardEmu as kbe
import threading
from classes.nfsbots.SimpleDriverBot import SimpleDriverBot

# Ждем три секунды, успеваем переключиться на окно:
print('waiting for 2 seconds...')
time.sleep(2)

#ВНИМАНИЕ! PyAutoGUI НЕ ЧИТАЕТ В JPG!
title = './nfs-shift-title.png'

# ВНИМАНИЕ!  У вас, скорее всего, будет другое разрешение, т.к. у меня 4К-монитор!
# Здесь надо выставить те параметры, которые вы задали в игре.
window_resolution = (1920, 1080)

nfs_window_location = None
searching_attempt = 1
while searching_attempt <= 5:
    nfs_window_location = pyautogui.locateOnScreen(title)

    if nfs_window_location is not None:
        print('nfs_window_location = ', nfs_window_location)
        break
    else:
        searching_attempt += 1
        time.sleep(1)
        print("attempt %d..." % searching_attempt)

if nfs_window_location is None:
    print('NFS Window not found')
    exit(1)


# Извлекаем из картинки-скриншота только данные окна NFS.
# Наша target-картинка - это заголовочная полоска окна. Для получения скриншота, мы берем ее левую точку (0),
# а к верхней (1) прибавляем высоту (3)
left = nfs_window_location[0]
top = nfs_window_location[1]+nfs_window_location[3]

window = (left, top, left+window_resolution[0], top+window_resolution[1])

ranges = {
    'min_h1': [0,  180],
    'max_h1': [180,180], # Как ни странно, вроде ни на что не влияет

    #'min_h2': [0, 180],
    #'max_h2': [0, 180],


    'min_s':  [0, 255],
    'max_s':  [8, 255],  # Видим только дорогу


    'min_v':  [0,   255],
    'max_v':  [118, 255],  # Видим только дорогу

    'matrix':  [9, 255],
    'tresh':  [8, 255],
    'iterations':  [8, 64],

    'wheel':  [0,1]
}


def set_handler_to_trackbar(name):
    def handler(x):
        global ranges
        ranges[name][0] = x
        print(*[(x, ranges[x][0]) for x in ranges if ranges[x][0] != ranges[x][1]])
    return handler


cv2.namedWindow('result')

for name, value in ranges.items():
    cv2.createTrackbar(name, 'result', 1 if name in ['matrix', 'tresh', 'iterations'] else 0, ranges[name][1], set_handler_to_trackbar(name))
    cv2.setTrackbarPos(name, 'result', value[0])



def getMask (hsv):
    mask1 = cv2.inRange(hsv, (ranges['min_h1'][0], ranges['min_s'][0], ranges['min_v'][0]), (ranges['max_h1'][0], ranges['max_s'][0], ranges['max_v'][0]))
    #mask2 = cv2.inRange(hsv, (ranges['min_h2'][0], ranges['min_s'][0], ranges['min_v'][0]), (ranges['max_h2'][0], ranges['max_s'][0], ranges['max_v'][0]))
    #return cv2.bitwise_or(mask1, mask2)
    return mask1


angle = None

driver = SimpleDriverBot()


@driver.get_data
def get_data():
    return angle


@driver.can_drive
def can_drive() -> bool:
    mouse = pyautogui.position()
    mouse_at_window = window[0] <= mouse[0] <= window[2] and  window[1] <= mouse[1] <= window[3]
    return ranges['wheel'][0] == 1 and mouse_at_window


while True:

    pix = pyautogui.screenshot(region=(left, top, window_resolution[0], window_resolution[1]))
    numpix = cv2.cvtColor(np.array(pix), cv2.COLOR_RGB2BGR)

    hsv = cv2.cvtColor(numpix, cv2.COLOR_BGR2HSV)
    mask = getMask(hsv)

    result = cv2.bitwise_and(numpix, numpix, mask=mask)
    result_copy = imutils.resize(result.copy(), width=800, height=450)
    result_copy = cv2.cvtColor(result_copy, cv2.COLOR_BGR2GRAY)

    # Отрезаем нахер нижнюю половину контура — она только шумит и мешает:
    result_copy[result_copy.shape[0]//2:,:] = 0

    # Нет эффекта
    # result_copy = cv2.bilateralFilter(result_copy, 5, 175, 175)


    matrix = (ranges['matrix'][0], ranges['matrix'][0])

    # Избавляемся от мелких объектов.

    # Обратная функции erode: если есть белый пиксель, весь контур становится белым.
    # Аналогично не работает.
    result_copy = cv2.dilate(result_copy, matrix, iterations=ranges['iterations'][0])

    # Уменньшаем контуры белых объектов: если в рамках матрицы есть "не белый" пиксель, то все становится черным.
    # Не работает вообще. Тестировать.
    result_copy = cv2.erode(result_copy, matrix, iterations=ranges['iterations'][0])


    # BLUR
    # В районе 45-45 просто отличный результат:
    # result_copy = cv2.blur(result_copy, matrix)
    # около 9 оптимум, более не надо.
    ret, result_copy = cv2.threshold(result_copy, ranges['tresh'][0], 150, cv2.THRESH_BINARY)
    # ~BLUR


    # Дает обратный эффект, надо исследовать.
    # result_copy = cv2.adaptiveThreshold(result_copy, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 15)

    # Ищем контуры
    # Сами структуры контуров хранятся в начальном элементе возвращаемого значения
    # (Это на винде, на Linux может быть другой индекс):
    contours = cv2.findContours(result_copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]

    # Их, кстати, может и не быть:
    if contours:
        # Сортируем по убыванию площади контура — хотим один самый большой:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # Третий аргумент — это индекс контура, который мы хотим вывести. Мы хотим самый большой.
        # Вывести все можно, передав -1 вместо 0:
        cv2.drawContours(result_copy, contours, 0, (255, ), 8)
        contour = contours[0]

        # Получаем прямоугольник, обрамляющий наш контур:
        (x, y, w, h) = cv2.boundingRect(contour)

        # И выводим его:
        cv2.rectangle(result_copy, (x, y), (x+w, y+h), (255, ), 1)


        start_y, start_x = result_copy.shape
        start_x //= 2


        # считаем моменты контура:
        M = cv2.moments(contour)

        # Центр тяжести это первый момент (сумма радиус-векторов), отнесенный к нулевому (площади-массе)
        if 0 != M['m00']:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.circle(result_copy, (cx, cy), 5, 255, 2)
            cv2.line(result_copy, (start_y, start_x), (cx, cy), (255, ), 2)
            tangen = start_x - cx
            normal = start_y - cy

            if normal != 0:
                angle = np.degrees(np.arctan(tangen / normal))
            else:
                angle = None

        cv2.line(result_copy, (start_y, start_x), (start_y, y+h//2), (255, ), 2)


    cv2.imshow('mask', imutils.resize(mask, width=1600, height=900))

    cv2.imshow('h', imutils.resize(hsv[:,:,0], width=800, height=450))
    cv2.imshow('s', imutils.resize(hsv[:,:,1], width=800, height=450))
    cv2.imshow('v', imutils.resize(hsv[:,:,2], width=800, height=450))


    cv2.imshow('result', imutils.resize(result_copy, width=1600, height=900))
    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()

driver.do_run = False
driver.thread.join()
