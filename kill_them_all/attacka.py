#!/bin/env python
# killa
# import gpio as roland
# 
# roland.init()
import numpy as np
import cv2

cv2.namedWindow('image')

firstFrame = None
cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    if not ret:
        print('Can\'t receive frame (stream end?). Exiting ...')
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if firstFrame is None:
        firstFrame = gray
        continue

    frameDelta = cv2.absdiff(firstFrame, gray)
    
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    s = 0
    for c in cnts:
        # print(c)
        (x, y, w, h) = cv2.boundingRect(c)
        s += w * h
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    print((f'{s=}'))
    if s > 10000:
        fh, fw, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (fw, fh), (0, 0, 255), 50)

    firstFrame = gray
    cv2.imshow('image', frame)

    if cv2.waitKey(1) == ord('q'):
        break

# cv2.destroyAllWindows()
