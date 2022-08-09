#!/bin/env python
from time import sleep
from dump import look
import cv2
import sys

cascPath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(1)
pitch = 0
yaw = 0

while True:
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        # flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    if not len(faces):
        continue

    h, w, _ = frame.shape

    fx, fy, fw, fh = faces[0]
    cx = fx + fw / 2
    cy = fy + fh / 2

    print(f'I can see your family at {cx} {cy}')

    max_x_d = (w / 2) ** 2
    max_y_d = (h / 2) ** 2

    dx = (cx - w / 2) ** 2
    dy = (cy - h / 2) ** 2

    dt = 30

    yaw   += dx / max_x_d * dt
    pitch += dy / max_y_d * dt

    if yaw > 90: yaw = 90
    elif yaw < -90: yaw = -90

    if pitch > 90: pitch = 90
    elif pitch < -90: pitch = -90

    look(yaw, pitch)

video_capture.release()
