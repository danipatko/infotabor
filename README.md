# infotabor 2022

All the stuff made in 2022.  

## Usage
Files under `pi/` are intended to be run on a Raspberry Pi, therefore using `RPi.GPIO`.  

### Color tracking 
Calibrate the desired color using `detect/getcols.py`. The calibration will be saved to `colors.csv`.  

Robot: `detect/pi/color.py`

Servo implementations:  
- Kristóf: `servo/pi/turn_1.py`
- Dapa: `servo/pi/turn_2.py`

*Note*: To get the servo working use the driver `PCA9685.py`, and make sure the `i2c` interface and legacy camera support is enabled in `raspi-config`.

### Motion tracking  
The robot dashes forward when any movement in the image is detected.  

`detect/pi/motion.py`  

### Posture (human) tracking with tflite   
The robot follows the closest human figure in its field of view.

Robot: `posture/pi/posture.py`  
*Note*: Running the script directly on the Raspberry causes delays due to the lack of computing power. Using a more powerful client resolved this issue.  

Client: `posture/posture_client.py`  

## Useful commands

May be useful later

### Find your Raspberry on the network:
```
nmap 192.168.1.0/24 -p 22 --open
# alternatively
nmap 192.168.1.0/24 -p 22 | grep -B 5 open
```

### Create video stream using netcat  

**On the camera device**
```
# Using ffmpeg
ffmpeg -f v4l2 -i /dev/video0 -f avi - | nc 192.168.1.123 1234
# Using raspivid
raspivid -fps 20 -t 99999999 -o - | nc 192.168.1.123 1234
```

**Receiving**
```
# Mplayer
nc -lvp 1234 | mplayer -
# Named pipe
nc -lvp 1234 > fifo
```

**OpenCV video capture from named pipe**
```py
cap = cv2.VideoCapture()
cap.open('fifo')
```


