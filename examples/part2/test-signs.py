import os
import numpy as np

ext='jpg'
path = '../../data/traffic-light'

for f in os.listdir(path):
    if f.endswith(ext):
        print(f)


def getMainColor(hist: bytearray) -> tuple:
    point = np.argmax(hist)

    color = None

    if point >=0 and point <= 14 or point > 160:
        color = 'red'
    elif point >= 15 and point < 35:
        color = 'yellow'
    #elif point >= 45 and point <= 75:
    elif point >= 36 and point <= 95:
        color = 'green'

    return color, point

