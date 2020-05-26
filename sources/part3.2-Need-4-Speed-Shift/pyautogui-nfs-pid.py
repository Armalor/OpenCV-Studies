import pyautogui
import time
import numpy as np
import cv2
import imutils
import classes.keyboardEmu as kbe
import threading
from classes.nfsbots.PidDriverBot import PidDriverBot

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
    'max_h1': [180, 180], # Как ни странно, вроде ни на что не влияет

    #'min_h2': [0, 180],
    #'max_h2': [0, 180],


    'min_s':  [3, 255],
    'max_s':  [17, 255],  # Видим только дорогу, 8 базовое значение


    'min_v':  [20,   255], #
    'max_v':  [255, 255],  # Видим только дорогу

    #'matrix':  [5, 255],
    #'tresh':  [21, 255],
    #'iterations':  [0, 64],

    'wheel':  [0,1],


}

koeff = {
    'linear': [0, 20, 11],
    'integral': [0, 20, 0],
    'diff': [0, 20, 2],
}


def set_handler_to_trackbar(name):
    def handler(x):
        global ranges
        ranges[name][0] = x
        print(*[(x, ranges[x][0]) for x in ranges if ranges[x][0] != ranges[x][1]])
    return handler

def set_handler_to_koeff(name):
    def handler(x):
        global koeff
        koeff[name][2] = x
        print(*[(x, koeff[x][2]) for x in koeff])
    return handler

cv2.namedWindow('result')

for name, value in ranges.items():
    cv2.createTrackbar(name, 'result', 1 if name in ['matrix', 'tresh'] else 0, ranges[name][1], set_handler_to_trackbar(name))
    cv2.setTrackbarPos(name, 'result', value[0])

for name, value in koeff.items():
    cv2.createTrackbar(name, 'result', value[0], value[1], set_handler_to_koeff(name))
    cv2.setTrackbarPos(name, 'result', value[2])

def getMask (hsv):
    mask1 = cv2.inRange(hsv, (ranges['min_h1'][0], ranges['min_s'][0], ranges['min_v'][0]), (ranges['max_h1'][0], ranges['max_s'][0], ranges['max_v'][0]))
    #mask2 = cv2.inRange(hsv, (ranges['min_h2'][0], ranges['min_s'][0], ranges['min_v'][0]), (ranges['max_h2'][0], ranges['max_s'][0], ranges['max_v'][0]))
    #return cv2.bitwise_or(mask1, mask2)
    return mask1

# Создаем бота-водителя
driver = PidDriverBot()

# Угол отклонения от нормали в градусах, по его величине меняем направление (x-компонента):
angle = None

# Длина радиус-вектора до центра масс контура (y-компонента управления):
radius = None


@driver.get_data
def get_data():
    return {'x': angle, 'y': radius}

@driver.get_multiplexors
def get_multiplexors():
    return {'linear': koeff['linear'][2], 'integral': koeff['integral'][2], 'diff': koeff['diff'][2]}

# Можем передать управление боту только если выставлен соответствующий ползунок «wheel» и мышь в пределах окна игры
@driver.can_drive
def can_drive() -> bool:
    mouse = pyautogui.position()
    mouse_at_window = window[0] <= mouse[0] <= window[2] and window[1] <= mouse[1] <= window[3]
    return ranges['wheel'][0] == 1 and mouse_at_window

prev_cx  = 0
prev_cy = 0
prev_area = 0

while True:

    pix = pyautogui.screenshot(region=(left, top, window_resolution[0], window_resolution[1]))
    numpix = cv2.cvtColor(np.array(pix), cv2.COLOR_RGB2BGR)

    hsv = cv2.cvtColor(numpix, cv2.COLOR_BGR2HSV)
    mask = getMask(hsv)

    result = cv2.bitwise_and(numpix, numpix, mask=mask)
    result_copy = imutils.resize(result.copy(), width=800)
    result_copy = cv2.cvtColor(result_copy, cv2.COLOR_BGR2GRAY)

    # Отрезаем нижнюю часть контура — она только шумит и мешает:
    result_copy[int(result_copy.shape[0] * 0.75):, :] = 0
    # Скрываем также верхнюю треть — информации там все равно нет:
    result_copy[:int(result_copy.shape[0] * 0.48), :] = 0
    # Убираем квдрат по центру, где отображаются спидометр-тахометр:
    #result_copy[result_copy.shape[0]-150:, int(result_copy.shape[1]//2-150) : int(result_copy.shape[1]//2+150)] = 0
    cv2.circle(result_copy, (result_copy.shape[1]//2-70, result_copy.shape[0]-100), 45, 0, 55)
    cv2.circle(result_copy, (result_copy.shape[1]//2+70, result_copy.shape[0]-100), 45, 0, 55)


    # Нет эффекта
    # result_copy = cv2.bilateralFilter(result_copy, 5, 175, 175)
    # matrix = (ranges['matrix'][0], ranges['matrix'][0])

    # Избавляемся от мелких объектов.

    # Обратная функции erode: если есть белый пиксель, весь контур становится белым.
    # Аналогично не работает.
    #result_copy = cv2.dilate(result_copy, matrix, iterations=ranges['iterations'][0])

    # Уменньшаем контуры белых объектов: если в рамках матрицы есть "не белый" пиксель, то все становится черным.
    # Не работает вообще. Тестировать.
    # if ranges['iterations'][0] > 0:
    #    result_copy = cv2.erode(result_copy, matrix, iterations=ranges['iterations'][0])

    # BLUR
    # В районе 45-45 просто отличный результат:
    #result_copy = cv2.blur(result_copy, matrix)
    # около 9 оптимум, более не надо.
    # ret, result_copy = cv2.threshold(result_copy, ranges['tresh'][0], 150, cv2.THRESH_BINARY)
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
        cv2.drawContours(result_copy, contours, 0, (255, ), 3)
        contour = contours[0]

        # Получаем прямоугольник, обрамляющий наш контур:
        (b_rect_x, b_rect_y, b_rect_w, b_rect_h) = cv2.boundingRect(contour)

        # И выводим его:
        cv2.rectangle(result_copy, (b_rect_x, b_rect_y), (b_rect_x+b_rect_w, b_rect_y+b_rect_h), (255, ), 1)

        start_y, start_x = result_copy.shape
        start_x //= 2

        # считаем моменты контура:
        M = cv2.moments(contour)


        # Центр тяжести это первый момент (сумма радиус-векторов), отнесенный к нулевому (площади-массе)
        if 0 != M['m00']:
            area = M['m00']
            cx = int(M['m10'] / area)
            cy = int(M['m01'] / area)
            cv2.circle(result_copy, (cx, cy), 5, 255, 2)
            cv2.line(result_copy, (start_x, start_y), (cx, cy), (255, ), 2)
            tangential = start_x - cx
            normal = start_y - cy

            if normal != 0:
                angle = np.degrees(np.arctan(tangential / normal))
            else:
                angle = None

            dr = np.sqrt((cx - prev_cx) ** 2 + (cy - prev_cy) ** 2)
            radius  = np.sqrt(cx**2+cy**2)
            prev_cx = cx
            prev_cy = cy

        else:
            area = 0.0
            dr = None
            radius = 0

        cv2.line(result_copy, (start_x, start_y), (start_x, b_rect_y+b_rect_h//2), (255, ), 2)

        font = cv2.FONT_HERSHEY_SIMPLEX
        left_bottom_corner_of_text = (10, 30)
        left_bottom_corner_of_text_dr = (10, 60)
        fontScale = 1
        fontColor = (255,)
        lineType = 1




        cv2.putText(result_copy, 'angle: %.2f' % angle,
                    left_bottom_corner_of_text,
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        if dr is not None and radius != 0.0:
            cv2.putText(result_copy, 'dr: %.2f%%' % (dr*100.0 / radius),
                        left_bottom_corner_of_text_dr,
                        font,
                        fontScale,
                        fontColor,
                        lineType)

    cv2.imshow('h', imutils.resize(hsv[:,:,0], width=800, height=450))
    cv2.imshow('s', imutils.resize(hsv[:,:,1], width=800, height=450))
    cv2.imshow('v', imutils.resize(hsv[:,:,2], width=800, height=450))

    cv2.imshow('mask', imutils.resize(mask, width=1600, height=900))
    cv2.imshow('result', imutils.resize(result_copy, width=1600, height=900))

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
driver.__del__()
