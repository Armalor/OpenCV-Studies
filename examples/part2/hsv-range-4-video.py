import cv2


# Функция-обработчик состояния трекбара (не делает ничего):
def doNothing(x):
    pass


cap = cv2.VideoCapture(0)

cv2.namedWindow('result')

cv2.createTrackbar('min_h', 'result', 0, 180, doNothing)
cv2.createTrackbar('min_s', 'result', 0, 255, doNothing)
cv2.createTrackbar('min_v', 'result', 0, 255, doNothing)

cv2.createTrackbar('max_h', 'result', 0, 180, doNothing)
cv2.createTrackbar('max_s', 'result', 0, 255, doNothing)
cv2.createTrackbar('max_v', 'result', 0, 255, doNothing)

cv2.setTrackbarPos('min_s', 'result', 100)
cv2.setTrackbarPos('min_v', 'result', 100)


cv2.setTrackbarPos('max_h', 'result', 180)
cv2.setTrackbarPos('max_s', 'result', 255)
cv2.setTrackbarPos('max_v', 'result', 255)

while True:
    ret, frame = cap.read()

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Размываем HSV-картинку с матрицей размытия 5*5
    frame_hsv = cv2.blur(frame_hsv, (5,5))


    min_h = cv2.getTrackbarPos('min_h', 'result')
    min_s = cv2.getTrackbarPos('min_s', 'result')
    min_v = cv2.getTrackbarPos('min_v', 'result')

    max_h = cv2.getTrackbarPos('max_h', 'result')
    max_s = cv2.getTrackbarPos('max_s', 'result')
    max_v = cv2.getTrackbarPos('max_v', 'result')

    mask = cv2.inRange(frame_hsv, (min_h, min_s, min_v), (max_h, max_s, max_v))

    # Избавляемся от мелких объектов.
    # Уменньшаем контуры белых объектов: если в рамках матрицы есть "не белый" пиксель, то все становится черным.
    matrix = (50,50)
    maskEr = cv2.erode(mask, matrix, iterations=8)
    # Обратная функции erode: если есть белый пиксель, весь контур становится белым.
    maskDi = cv2.dilate(maskEr, matrix, iterations=8)
    # Избавились.

    result = cv2.bitwise_and(frame, frame, mask=maskDi)
    result_hsv = cv2.bitwise_and(frame_hsv, frame_hsv, mask=maskDi)


    cv2.imshow('mask', mask)
    cv2.imshow('maskDi', maskDi)
    cv2.imshow('result', result)
    cv2.imshow('result_hsv', result_hsv)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()