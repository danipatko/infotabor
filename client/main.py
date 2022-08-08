#!/bin/env python

from websocket import create_connection

def clamp(val:int, _min:int, _max:int):
    return min(_min, max(_max, val))

class Robot:
    port: int
    host: str

    def __init__(self, host = 'localhost', port = 1111):
        self.host = host
        self.port = port
        self.ws = create_connection(f'ws://{self.host}:{self.port}/ws')

    # Close the websocket connection
    def close(self):
        self.ws.close()

    # Set a pin to high or low, logic can be 0 or 1
    def pin(self, pin: int, logic: 0 | 1):
        self.ws.send(f'p {pin} {logic}')
    
    # Configure a software pwm on a pin, hz is the frequency, and cycle is the duty cycle, a number between 0 and 100
    def pwm(self, pin: int, hz: int, cycle: int):
        self.ws.send(f'w {pin} {hz} {cycle}')
    
    # Move the robot's left and right motors with the given speed
    def move(self, left: int, right: int):
        left = clamp(left, 0, 100)
        right = clamp(right, 0, 100)
        self.ws.send(f'm {left} {right}')

    # Stop the robot
    def stop(self):
        self.ws.send('s')
    
    # Set the leds to the given color, r,g,b can be 0 or 1
    def led(self, rgb = [0,0,0]):
        for i in range(len(rgb)):
            rgb[i] = clamp(rgb[i], 0, 1)
        self.ws.send(f'l {rgb[0]} {rgb[1]} {rgb[2]}')

    # Set the servo to the given absolute angle
    def servo(self, angle:int):
        angle = clamp(angle, -180, 180)
        self.ws.send(f'v {angle}')

    # Sounds the buzzer at the given frequency
    def buzzer(self, freq: int):
        freq = clamp(freq, 0, 100)
        self.ws.send(f'b {freq}')

    # Get the data from the four onboard sensors in four (0|1) numbers
    def sensors(self):
        self.ws.send('t')
        values = self.ws.recv()
        return map(lambda x: int(x), values.split(','))
    
    # Stop robot and disconnect
    def panic(self):
        self.stop()
        self.close()


client = Robot()
print('connected')
client.move(10, 20)
print('called move')
client.stop()
print('called stop')
client.close()
print('called close')
