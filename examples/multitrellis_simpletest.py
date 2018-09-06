import time

from board import SCL, SDA
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

#create the i2c object for the trellis
i2c_bus = busio.I2C(SCL, SDA)

#create the trellis
trelli = [ 
            [ NeoTrellis(i2c_bus, False, addr=0x2E), NeoTrellis(i2c_bus, False, addr=0x2F) ],
            [ NeoTrellis(i2c_bus, False, addr=0x30), NeoTrellis(i2c_bus, False, addr=0x61) ]
         ]

trellis = MultiTrellis(trelli)

#some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

#this will be called when button events are received
def blink(x,y,edge):
    #turn the LED on when a rising edge is detected
    if edge == NeoTrellis.EDGE_RISING:
        trellis.color(x, y, BLUE)
    #turn the LED off when a rising edge is detected
    elif edge == NeoTrellis.EDGE_FALLING:
        trellis.color(x, y, OFF)

for y in range(8):
    for x in range(8):
        #activate rising edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        #activate falling edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x, y, blink)
        trellis.color(x, y, PURPLE)
        time.sleep(.05)

for y in range(8):
    for x in range(8):
        trellis.color(x, y, OFF)
        time.sleep(.05)
        pass

while True:
    #the trellis can only be read every 17 millisecons or so
    trellis.sync()
    time.sleep(.02)
