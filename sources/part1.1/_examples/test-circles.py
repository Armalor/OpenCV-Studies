import cv2
from matplotlib import pyplot as plt
import numpy as np
import time
import imutils


# green = np.uint8 ([[[0,255,0]]])
# hsv_green = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
# print ('green', hsv_green, sep=': ')
#
# yellow = np.uint8 ([[[128  , 128, 0]]])
# hsv_yellow = cv2.cvtColor(yellow, cv2.COLOR_BGR2HSV)
# print ('yellow', hsv_yellow, sep=': ')
#
# red = np.uint8 ([[[255 , 0, 0], [1, 0, 0]]])
# hsv_red = cv2.cvtColor(red, cv2.COLOR_BGR2HSV)
# print ('red', hsv_red, sep=': ')

def getMainColor(hist: bytearray) -> tuple:
    point = np.argmax(hist)

    color = None

    if point >= 0 and point <= 14 or point > 160:
        color = 'red'
    elif point >= 15 and point < 35:
        color = 'yellow'
    #elif point >= 45 and point <= 75:
    elif point >= 36 and point <= 95:
        color = 'green'

    return color, point

color = 'red'
number = 3

rgb = cv2.imread('../../../data/traffic-light/'+color+'/light-'+str(number)+'-'+color+'.jpg')

height, width, depth = rgb.shape
newWidth = 400
newHeight = (newWidth * height) // width

rgb = imutils.resize(rgb, width=newWidth)
rgbCopy = rgb.copy()
hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)

def getMask (hsv):
    s_low = 100
    # определить диапазон и маску зеленого цвета в HSV
    lower_g = np.array([36, 50, 100])
    upper_g = np.array([95, 255, 255])
    mask_g = cv2.inRange(hsv, lower_g, upper_g)

    # определить диапазон и маску желтого цвета в HSV
    lower_y = np.array([15, 100, 100])
    upper_y = np.array([35, 255, 255])
    mask_y = cv2.inRange(hsv, lower_y, upper_y)

    # определить диапазон и маску красного цвета в HSV (красный цвет с обоих концов, поэтому маски красного - две)
    lower_r0 = np.array([0, 50, 50])
    upper_r0 = np.array([14, 255, 255])
    mask_r0 = cv2.inRange(hsv, lower_r0, upper_r0)

    lower_r1 = np.array([160, 50, 50])
    upper_r1 = np.array([180, 255, 255])
    mask_r1 = cv2.inRange(hsv, lower_r1, upper_r1)

    mask = cv2.bitwise_or(mask_r0, mask_r1)
    mask = cv2.bitwise_or(mask, mask_y)
    mask = cv2.bitwise_or(mask, mask_g)

    return mask


mask = getMask(hsv)

# lower_all = np.array([0, 100, 100])
# upper_all = np.array([255, 255, 255])
# mask = cv2.inRange(hsv, lower_all, upper_all)

# Побитовая-И-маска и исходное изображение
res = cv2.bitwise_and(rgb, rgb, mask=mask)

gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
bilateral_filtered_gray = cv2.bilateralFilter(gray, 5, 175, 175)

circles = cv2.HoughCircles(bilateral_filtered_gray,cv2.HOUGH_GRADIENT,1,newHeight, param1=225,param2=15,minRadius=0,maxRadius=newHeight//3)
roImgExists = False
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:

        x1 = i[0]-i[2]
        y1 = i[1]-i[2]

        x2 = i[0]+i[2]
        y2 = i[1]+i[2]
        topLeft = (x1,y1)
        bottomRight = (x2,y2)


        roImg = rgbCopy[y1:y2, x1:x2]
        roImgExists = True

        cv2.circle(res,(i[0],i[1]),i[2],(255,255,255),2)
        cv2.rectangle(res, topLeft, bottomRight, (0, 255, 0), 2)


        #draw the center of the circle
        #cv2.circle(res,(i[0],i[1]),2,(0,0,255),3)









if roImgExists:
    roImg_hsv = cv2.cvtColor(roImg, cv2.COLOR_BGR2HSV)
    roImg_mask = getMask(roImg_hsv)

    hist = cv2.calcHist([roImg_hsv], [0], roImg_mask, [180], [0, 180])
    plt.plot(hist, color='gray')
    plt.xlim([0, 180])
    plt.ylim([0, 2000])
    plt.show()

    color = getMainColor(hist)
    print(*color)



# Без этого sleep imshow стартует слишком рано и картинки получаются в свернутом виде
time.sleep(1)


cv2.imshow('img', rgb)
cv2.imshow('mask', mask)
cv2.imshow('gray', bilateral_filtered_gray)
cv2.imshow('res', res)
if roImgExists:
    cv2.imshow('roImg', roImg)


while 1:
    if cv2.waitKey(1) == 27:
        break


cv2.destroyAllWindows()

