#!/bin/env python
from os.path import exists
from client import Robot
import numpy as np
import time
import cv2
import sys

# Default hsv configured for red
HSV_MIN = np.array([0, 93, 237])
HSV_MAX = np.array([179, 255, 255])

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
# Supposing the camera is looking forward
CENTER = FRAME_WIDTH // 2
# Detection offset in px
OFFSET = 50
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


# Get the direction to turn towards
# Returns -1 left, 0 don't turn, 1 right
def get_direction(object_x:int, center_x:int):
    if object_x - center_x - OFFSET > 0:
        return 1
    elif object_x - center_x + OFFSET < 0:
        return -1
    else:
        return 0


cv2.namedWindow('image')

# show_original = True

# Open camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not cap.isOpened():
    print('Unable to open video capture. Maybe try another video index?')
    exit(1)

client = Robot()

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
        direction = get_direction(center[0], CENTER)
        
        if direction == 0:
            # Dash forward
            client.move(100, 100)
            time.sleep(3)
            # Stop & continue searching
            client.stop()
            search = True
        else:
            # Turn towards target
            client.move(direction * TURN_SPEED, -direction * TURN_SPEED)
    
    # Start searching (do not send move command every frame)
    if search:
        search = False
        client.move(-TURN_SPEED, TURN_SPEED)

    cv2.imshow('image', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
