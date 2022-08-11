"""
Run Pose detection with Camera, Press ESC to exit the program
For Raspberry PI, please use `import tflite_runtime.interpreter as tflite` instead
"""
import re
import cv2
import numpy as np
import signal
from client import Robot

roland = Robot(host='192.168.1.127')

import tensorflow.lite as tflite
# import tflite_runtime.interpreter as tflite

from PIL import Image

def cleanup(*args):
    roland.stop()
    roland.close()
    exit(0)

signal.signal(signal.SIGINT, cleanup)

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CENTER = CAMERA_WIDTH // 2
SPEED = 0.8


def sigmoid(x):
    return 1.0 / (1.0 + 1.0 / np.exp(x))


def load_model(model_path):
    r"""Load TFLite model, returns a Interpreter instance."""
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


def process_image(interpreter, image, input_index):
    r"""Process an image, Return a list of positions in a 4-Tuple (pos_x, pos_y, offset_x, offset_y)"""
    input_data = np.expand_dims(image, axis=0)  # expand to 4-dim
    input_data = (np.float32(input_data) - 127.5) / 127.5  # float point

    # Process
    interpreter.set_tensor(input_index, input_data)
    interpreter.invoke()

    # Get outputs
    output_details = interpreter.get_output_details()
    # print(output_details)

    output_data = np.squeeze(interpreter.get_tensor(output_details[0]['index']))
    offset_data = np.squeeze(interpreter.get_tensor(output_details[1]['index']))

    points = []
    total_row, total_col, total_points = output_data.shape

    # totally 17 points, only legs are relevant: 9 -> 17
    for k in range(0, total_points):
        max_score = output_data[0][0][k]
        max_row = 0
        max_col = 0
        for row in range(total_row):
            for col in range(total_col):
                if (output_data[row][col][k] > max_score):
                    max_score = output_data[row][col][k]
                    max_row = row
                    max_col = col

        points.append((max_row, max_col))
        # print(sigmoid(max_score))

    positions = []
    confidence = 0

    for idx, point in enumerate(points):
        pos_y, pos_x = point

        # y is row, x is column
        offset_x = offset_data[pos_y][pos_x][idx + 17]
        offset_y = offset_data[pos_y][pos_x][idx]

        positions.append((pos_x, pos_y, offset_x, offset_y))
        confidence += sigmoid(output_data[pos_y][pos_x][idx])

    confidence = confidence / len(points)
    return positions, confidence


def get_position(positions, frame):
    r"""Display Detected Points in circles"""
    sum_x = 0
    sum_y = 0

    for pos in positions:
        pos_x, pos_y, offset_x, offset_y = pos

        # Calculating the x and y coordinates
        x = int(pos_x / 8 * CAMERA_WIDTH + offset_x)
        y = int(pos_y / 8 * CAMERA_HEIGHT + offset_y)

        sum_x += x
        sum_y += y
    
    res = (sum_x // len(positions), sum_y // len(positions))
    
    cv2.circle(frame, res, 5, (255, 0, 0), 3)
    cv2.imshow('image', frame)

    return res


if __name__ == "__main__":

    model_path = 'data/model.tflite'
    cap = cv2.VideoCapture(2)
    cv2.namedWindow('image')

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 10) # Limit frame rate so the ws client does not crash

    interpreter = load_model(model_path)
    input_details = interpreter.get_input_details()

    # Get Width and Height
    input_shape = input_details[0]['shape']
    height = input_shape[1]
    width = input_shape[2]

    # Get input index
    input_index = input_details[0]['index']

    # Process Stream
    while True:
        ret, frame = cap.read()

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image = image.resize((width, height))

        positions, conf = process_image(interpreter, image, input_index)

        if conf < 0.05:
            print('Not confident enough')
            roland.stop()
            continue
    
        (x, y) = get_position(positions, frame)

        speed_left = (x / CAMERA_WIDTH * 100) * SPEED
        speed_right = (100 - (x / CAMERA_WIDTH * 100)) * SPEED

        print(f'{x=} {y=} -> ({speed_left},{speed_right})')
        roland.move(speed_left, speed_right)

        key = cv2.waitKey(1)
        if key == 27:  # esc
            break

    cap.release()
