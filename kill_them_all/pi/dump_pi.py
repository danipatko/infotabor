import RPi.GPIO as GPIO
import signal

def cleanup(*args):
    GPIO.cleanup()
    exit(0)

signal.signal(signal.SIGINT, cleanup)
GPIO.setmode(GPIO.BOARD)

OUT_PIN_1 = 11
OUT_PIN_2 = 13
PULSE_FREQ = 50

GPIO.setup(OUT_PIN_1, GPIO.OUT)
GPIO.setup(OUT_PIN_2, GPIO.OUT)

s1 = GPIO.PWM(OUT_PIN_1, PULSE_FREQ)
s2 = GPIO.PWM(OUT_PIN_2, PULSE_FREQ)

s1.start(0)
s2.start(0)

def look(yaw: float, pitch: float):
    s1.ChangeDutyCycle((90 - yaw) / 18 + 2)
    s2.ChangeDutyCycle((90 - pitch) / 18 + 2)

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

for OUT_PIN in range(40):

    try:
        print(f'Trying pin {OUT_PIN}')
        PULSE_FREQ = 50

        print('Setting up')
        GPIO.setup(OUT_PIN, GPIO.OUT)

        print('Creating PWM')
        s = GPIO.PWM(OUT_PIN, PULSE_FREQ)
        print('Starting')
        s.start(0)

        def look(a: float): s.ChangeDutyCycle((90 - a) / 18 + 2)

        print('look(0)')
        look(0)
        time.sleep(1)

        print('look(45)')
        look(45)
        time.sleep(1)

        print('Stopping')
        s.stop()

        print('\n')
    except Exception as e:
        print('\n\n--------------------')
        print(e)
        print('--------------------\n\n')

print('Cleaning up')
GPIO.cleanup()