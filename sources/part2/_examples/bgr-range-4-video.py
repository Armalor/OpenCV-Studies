import cv2

# Функция-обработчик состояния трекбара (не делает ничего):
def doNothing(x):
    pass


cap = cv2.VideoCapture(0)

cv2.namedWindow('result')

cv2.createTrackbar('min_b', 'result', 0, 255, doNothing)
cv2.createTrackbar('min_g', 'result', 0, 255, doNothing)
cv2.createTrackbar('min_r', 'result', 0, 255, doNothing)

cv2.createTrackbar('max_b', 'result', 0, 255, doNothing)
cv2.createTrackbar('max_g', 'result', 0, 255, doNothing)
cv2.createTrackbar('max_r', 'result', 0, 255, doNothing)

cv2.setTrackbarPos('max_b', 'result', 255)
cv2.setTrackbarPos('max_g', 'result', 255)
cv2.setTrackbarPos('max_r', 'result', 255)

while True:
    ret, frame = cap.read()

    min_b = cv2.getTrackbarPos('min_b', 'result')
    min_g = cv2.getTrackbarPos('min_g', 'result')
    min_r = cv2.getTrackbarPos('min_r', 'result')

    max_b = cv2.getTrackbarPos('max_b', 'result')
    max_g = cv2.getTrackbarPos('max_g', 'result')
    max_r = cv2.getTrackbarPos('max_r', 'result')

    mask = cv2.inRange(frame, (min_b, min_g, min_r), (max_b, max_g, max_r))
    cv2.imshow('Mask', mask)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow('result', result)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()