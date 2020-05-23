import pyautogui
import time
import numpy as np
import cv2
import imutils

# Ждем три секунды, успеваем переключиться на окно:
print('ready for 3 seconds...')
time.sleep(3)

# ВНИМАНИЕ! PyAutoGUI НЕ ЧИТАЕТ В JPG! Проверьте сами!
title = './nfs-shift-title.png'
nfs_window_location = pyautogui.locateOnScreen(title)

print(nfs_window_location)

# Если не нашли окно, прекращаем работу:
if nfs_window_location is None:
    exit(1)

# Извлекаем из картинки-скриншота только данные окна NFS.
# Наша target-картинка - это заголовочная полоска окна. Для получения скриншота, мы берем ее левую точку (0),
# а к верхней (1) прибавляем высоту (3)
left = nfs_window_location[0]
top = nfs_window_location[1]+nfs_window_location[3]


ranges = {
    'min_h1': [51, 180],
    'max_h1': [77, 180],

    'min_h2': [72, 180],
    'max_h2': [41, 180],


    'min_s':  [27, 255],
    'max_s':  [255, 255],


    'min_v':  [0, 255],
    'max_v':  [255, 255],
}


def set_handler_to_trackbar(name):
    def handler(x):
        global ranges
        ranges[name][0] = x
        print(*[(x, ranges[x][0]) for x in ranges if ranges[x][0] != ranges[x][1]])
    return handler


cv2.namedWindow('result')

for name, value in ranges.items():
    cv2.createTrackbar(name, 'result', 0, ranges[name][1], set_handler_to_trackbar(name))
    cv2.setTrackbarPos(name, 'result', value[0])

def getMask (hsv):
    mask1 = cv2.inRange(hsv, (ranges['min_h1'][0], ranges['min_s'][0], ranges['min_v'][0]), (ranges['max_h1'][0], ranges['max_s'][0], ranges['max_v'][0]))
    mask2 = cv2.inRange(hsv, (ranges['min_h2'][0], ranges['min_s'][0], ranges['min_v'][0]), (ranges['max_h2'][0], ranges['max_s'][0], ranges['max_v'][0]))
    return cv2.bitwise_or(mask1, mask2)

while True:
    # ВНИМАНИЕ!  У вас, скорее всего, будет другое разрешение, т.к. у меня 4К-монитор!
    # Здесь надо выставить те параметры, которые вы задали в игре.
    window_resolution = (640, 480)
    pix = pyautogui.screenshot(region=(left, top, window_resolution[0], window_resolution[1]))
    numpix = np.array(pix)

    hsv = cv2.cvtColor(numpix, cv2.COLOR_BGR2HSV)
    mask = getMask(hsv)


    def where_to_turn(res):

        height = res.shape[0]
        width = res.shape[1]
        left = res[:height, :width // 2].sum()
        right = res[:height, width // 2:].sum()
        dif = left / right
        print(dif)
        return dif

    result = cv2.bitwise_and(numpix, numpix, mask=mask)



    result = imutils.resize(result, width=640, height=480)
    direct = where_to_turn(result)
    # pyautogui.keyDown('up')
    pyautogui.press('esc')
    if direct>1.2:
        pyautogui.keyDown('left')
        print('left')
    elif direct<0.8:
        pyautogui.keyDown('right')
        print('right')
    cv2.imshow('result', result)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()