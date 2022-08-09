import RPi.GPIO as GPIO
import signal
import time

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

