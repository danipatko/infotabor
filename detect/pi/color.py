#!/bin/env python
from os.path import exists
import gpio as roland
import numpy as np
import time
import cv2
import sys

def cleanup(*args):
    roland.motor(0, 0)
    roland.clean_up()
    exit(0)

signal.signal(signal.SIGINT, cleanup)

# Default hsv configured for red
HSV_MIN = np.array([0, 93, 237])
HSV_MAX = np.array([179, 255, 255])

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
# Supposing the camera is looking forward
CENTER = FRAME_WIDTH // 2
# Detection offset in px
OFFSET = 40
TURN_SPEED = 60

# Read config from colors.csv
if exists('colors.csv'):
    with open('colors.csv') as f:
        vals = np.array([* map(int, f.read().split(',')) ])
        HSV_MIN = vals[:3] ; HSV_MAX = vals[3:]

# Get the center of the tracked area of the image
# Returns the coordinates of the center and the annotated frame
def get_center(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HSV_MIN, HSV_MAX)
    M = cv2.moments(mask)

    # Center of masked object
    if M['m00'] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv2.circle(frame, (cX, cY), 5, (0, 255, 0), -1)
        return (cX, cY), frame
    else:
        return None, frame


# Open camera
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not cap.isOpened():
    print('Unable to open video capture. Maybe try another video index?')
    exit(1)

search = True

while True:
    ret, frame = cap.read()
    if not ret:
        print('Unable to receive frame from camera.')
        break

    center, frame = get_center(frame)

    # Target is picked up
    if center is not None:
        search = False
        
        (x, y) = get_position(positions, frame)

        speed_left = (x / FRAME_WIDTH * 100) * SPEED
        speed_right = (100 - (x / FRAME_WIDTH * 100)) * SPEED

        print(f'{x=} {y=} -> ({speed_left},{speed_right})')
        roland.motor(speed_left, speed_right)
    else:
        roland.motor(0, 0)

cv2.destroyAllWindows()
