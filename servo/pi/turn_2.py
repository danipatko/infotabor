#!/usr/bin/python
from PCA9685 import PCA9685
from os.path import exists
import RPi.GPIO as GPIO
import numpy as np
import signal
import time
import math
import cv2

def cleanup(*args):
    pwm.exit_PCA9685()
    exit(0)

signal.signal(signal.SIGINT, cleanup)

pwm = PCA9685()
pwm.setPWMFreq(50)
# pwm.setServoPulse(1, 500)

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


def look(yaw: float, pitch: float) -> None:
    pwm.setRotationAngle(1, yaw)
    pwm.setRotationAngle(0, pitch)

def lerp(v0:float, v1:float, t:float):
    return (1 - t) * v0 + t * v1;


CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CENTER_X = CAMERA_WIDTH // 2
CENTER_Y = CAMERA_HEIGHT // 2
TURN_SPEED = 0.2

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

max_yaw = (10, 170)
max_pitch = (10, 80)

yaw = 90
pitch = 35
look(yaw, pitch)
time.sleep(1)

# Open camera
if not cap.isOpened():
    print('Unable to open video capture. Maybe try another video index?')
    exit(1)

# Get cam point clamped between -1, 1
def get_point(screen_x: int, screen_y: int):
    x = (screen_x - CENTER_X) / CENTER_X
    y = (screen_y - CENTER_Y) / CENTER_Y
    return x, y

# Convert -1, 1 value to 10, 170
def convert_point(v: float, _max:(float, float), rev=False):
    if rev: return 10 + (170 - (v + 1) * (170 / 2))
    else: return _max[0] + (v + 1) * (_max[1] / 2)

i = 0
while i == 0:
    ret, frame = cap.read()
    if not ret:
        print('Unable to receive frame from camera.')
        break

    center = get_center(frame)
    if center is None:
        continue
    # i += 1
    
    cx, cy = center
    x, y = get_point(cx, cy)
    print(f'I can see your family at {cx:.2f} ({x:.2f}) | {cy:.2f} ({y:.2f})')

    zs_x = convert_point(x, max_yaw, rev=True)
    zs_y = convert_point(y, max_pitch)
    
    yaw = lerp(yaw, zs_x, TURN_SPEED)
    pitch = lerp(pitch, zs_y, TURN_SPEED)
    
    print(f'Looking at {yaw:.2f} {pitch:.2f}')
    
    look(yaw, pitch)

    time.sleep(0.05)

cleanup()