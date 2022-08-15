#!/bin/env python
from os.path import exists
import numpy as np
import cv2
import sys

cv2.namedWindow('image')

# Default hsv configured for red
hsv_min = np.array([0, 93, 237])
hsv_max = np.array([179, 255, 255])

# Read config from colors.csv
if exists('colors.csv'):
    with open('colors.csv') as f:
        vals = np.array([* map(int, f.read().split(',')) ])
        hsv_min = vals[:3] ; hsv_max = vals[3:]

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('Unable to open video capture. Maybe try another video index?')
    exit(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print('Unable to receive frame from camera.')
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    M = cv2.moments(mask)

    # Center of masked object
    if M['m00'] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv2.circle(frame, (cX, cY), 5, (0, 255, 0), -1)    

    cv2.imshow('image', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
