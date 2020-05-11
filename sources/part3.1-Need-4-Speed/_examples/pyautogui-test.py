import pyautogui
import time
import numpy as np

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


# ВНИМАНИЕ!  У вас, скорее всего, будет другое разрешение, т.к. у меня 4К-монитор!
# Здесь надо выставить те параметры, которые вы задали в игре.
window_resolution = (1920, 1080)

im = pyautogui.screenshot(region=(left, top, window_resolution[0], window_resolution[1]))
im.save('./nfs_shift_screenshots/test.png')

pix = np.array(im)
print(pix)
