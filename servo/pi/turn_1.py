#!/usr/bin/python
from PCA9685 import PCA9685
from os.path import exists
import RPi.GPIO as GPIO
import numpy as np
import signal
import time
import cv2

def cleanup(*args):
    pwm.exit_PCA9685()
    exit(0)

signal.signal(signal.SIGINT, cleanup)

pwm = PCA9685()
pwm.setPWMFreq(50)
pwm.setServoPulse(1, 500)

# Default hsv configured for red
HSV_MIN = np.array([0, 93, 237])
HSV_MAX = np.array([179, 255, 255])

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
        return (cX, cY)
    else:
        return None

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('Unable to open video capture. Maybe try another video index?')
    exit(1)

def look(yaw: float, pitch: float) -> None:
    yaw += 90
    pitch += 90

    if yaw > 170: yaw = 170
    elif yaw < 10: yaw = 10

    if pitch > 180: pitch = 180
    elif pitch < 10: pitch = 10

    print(f'yaw={yaw:.2f} pitch={pitch:.2f}', end='\r')
    pwm.setRotationAngle(1, yaw)
    pwm.setRotationAngle(0, pitch)

yaw = 0
pitch = 0
look(yaw, pitch)

while True:
    ret, frame = cap.read()
    if not ret:
        print('Unable to receive frame from camera.')
        break

    h, w, _ = frame.shape
    
    center = get_center(frame)
    if center is None:
        continue
    cx, cy = center

    print(f'I can see your family at {cx:.2f} {cy:.2f} ', end='')

    max_x_d = (w / 2) ** 2
    max_y_d = (h / 2) ** 2

    dx = (cx - w / 2) ** 2
    dy = (cy - h / 2) ** 2

    dt = 15

    yaw   -= dx / max_x_d * dt
    pitch -= dy / max_y_d * dt

    if yaw > 90: yaw = 90
    elif yaw < -90: yaw = -90

    if pitch > 90: pitch = 90
    elif pitch < -90: pitch = -90

    look(yaw, pitch)
    time.sleep(0.05)

cleanup()