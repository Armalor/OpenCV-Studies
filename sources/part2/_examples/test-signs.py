import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    print(ret)

    cv2.imshow('Frame',frame)

    mask = cv2.inRange(frame, (100,100,0), (255,255,255))
    cv2.imshow('Mask', mask)

    if cv2.waitKey(1) == 27: break

cap.release()
cv2.destroyAllWindows()