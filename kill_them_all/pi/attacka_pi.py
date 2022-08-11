#!/bin/env python
# killa

import gpio as roland
import numpy as np
import cv2
import sys
import time

MOVEMENT_SENS = 10000
# attacka speed and time
SPEED_FWD = 20
TIME_FWD = 2
# wait time after attacka
TIME_WAIT = 1
# speed and time backwards
TIME_BACK = 5
SPEED_BACK = 20
# time to wait after rolling back
TIME_IDLE = 5 

# roland.init()

def cleanup(*args):
    # roland.motor(0, 0)
    # roland.clean_up()
    exit(0)

signal.signal(signal.SIGINT, cleanup)
cap = cv2.VideoCapture(0)
firstFrame = None

while True:

    # Wait until movement
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

        # Sum of total diff area
        s = 0
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            s += w * h
        
        print((f'{s=}'))
        if s > MOVEMENT_SENS:
            break
    
        firstFrame = gray

    # Move back and forth
    print(f'I am coming for your family {s}')
    # roland.motor(SPEED_FWD, SPEED_FWD)
    time.sleep(TIME_FWD)
    print(f'Stopping')
    # roland.motor(0, 0)
    time.sleep(TIME_WAIT)
    print(f'Going home')
    # roland.motor(-SPEED_BACK, -SPEED_BACK)
    time.sleep(TIME_BACK)
    print(f'Idling')
    time.sleep(TIME_IDLE)

    if cv2.waitKey(1) == ord('q'):
        cleanup()

