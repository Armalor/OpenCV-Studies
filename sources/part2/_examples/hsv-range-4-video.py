import cv2


# Функция-обработчик состояния трекбара (не делает ничего):
def doNothing(x):
    pass


cap = cv2.VideoCapture(0)

cv2.namedWindow('result')

cv2.createTrackbar('min_h1', 'result', 0, 180, doNothing)
cv2.createTrackbar('min_h2', 'result', 0, 180, doNothing)
cv2.createTrackbar('min_s', 'result', 0, 255, doNothing)
cv2.createTrackbar('min_v', 'result', 0, 255, doNothing)

cv2.createTrackbar('max_h1', 'result', 0, 180, doNothing)
cv2.createTrackbar('max_h2', 'result', 0, 180, doNothing)
cv2.createTrackbar('max_s', 'result', 0, 255, doNothing)
cv2.createTrackbar('max_v', 'result', 0, 255, doNothing)

cv2.setTrackbarPos('min_s', 'result', 100)
cv2.setTrackbarPos('min_v', 'result', 100)



cv2.setTrackbarPos('min_h1', 'result', 1)
cv2.setTrackbarPos('min_h2', 'result', 160)
cv2.setTrackbarPos('max_h1', 'result', 14)
cv2.setTrackbarPos('max_h2', 'result', 180)
cv2.setTrackbarPos('max_s', 'result', 255)
cv2.setTrackbarPos('max_v', 'result', 255)

while True:
    ret, frame = cap.read()

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Размываем HSV-картинку с матрицей размытия 5*5
    frame_hsv = cv2.blur(frame_hsv, (5,5))


    min_h1 = cv2.getTrackbarPos('min_h1', 'result')
    min_h2 = cv2.getTrackbarPos('min_h2', 'result')
    min_s = cv2.getTrackbarPos('min_s', 'result')
    min_v = cv2.getTrackbarPos('min_v', 'result')

    max_h1 = cv2.getTrackbarPos('max_h1', 'result')
    max_h2 = cv2.getTrackbarPos('max_h2', 'result')
    max_s = cv2.getTrackbarPos('max_s', 'result')
    max_v = cv2.getTrackbarPos('max_v', 'result')

    mask1 = cv2.inRange(frame_hsv, (min_h1, min_s, min_v), (max_h1, max_s, max_v))
    mask2 = cv2.inRange(frame_hsv, (min_h2, min_s, min_v), (max_h2, max_s, max_v))
    mask = cv2.bitwise_or(mask1, mask2)


    # Избавляемся от мелких объектов.
    # Уменньшаем контуры белых объектов: если в рамках матрицы есть "не белый" пиксель, то все становится черным.
    matrix = (3,3)
    maskEr = cv2.erode(mask, matrix, iterations=2)
    # Обратная функции erode: если есть белый пиксель, весь контур становится белым.
    maskDi = cv2.dilate(maskEr, matrix, iterations=8)
    # Избавились.

    result = cv2.bitwise_and(frame, frame, mask=maskDi)
    result_hsv = cv2.bitwise_and(frame_hsv, frame_hsv, mask=maskDi)

    cv2.imshow('mask', mask)
    cv2.imshow('maskDi', maskDi)
    cv2.imshow('result', result)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()