import time

import board
import busio
from adafruit_neotrellis.neotrellism4 import NeoTrellisM4


#create the trellis
trellis_left = NeoTrellisM4()
trellis_right = NeoTrellisM4(left_part=trellis_left)

#some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

#this will be called when button events are received
def blink(event):
    #turn the LED on when a rising edge is detected
    if event.edge == NeoTrellisM4.EDGE_RISING:
        trellis_left.pixels[event.number] = CYAN
    #turn the LED off when a rising edge is detected
    elif event.edge == NeoTrellisM4.EDGE_FALLING:
        trellis_left.pixels[event.number] = OFF

for i in range(16):
    #activate rising edge events on all keys
    trellis_left.activate_key(i, NeoTrellisM4.EDGE_RISING)
    #activate falling edge events on all keys
    trellis_left.activate_key(i, NeoTrellisM4.EDGE_FALLING)
    #set all keys to trigger the blink callback
    trellis_left.callbacks[i] = blink

    #cycle the LEDs on startup
    trellis_left.pixels[i] = PURPLE
    time.sleep(.05)

for i in range(16):
    trellis_left.pixels[i] = OFF
    time.sleep(.05)

for i in range(16):
    #activate rising edge events on all keys
    trellis_right.activate_key(i, NeoTrellisM4.EDGE_RISING)
    #activate falling edge events on all keys
    trellis_right.activate_key(i, NeoTrellisM4.EDGE_FALLING)
    #set all keys to trigger the blink callback
    trellis_right.callbacks[i] = blink

    #cycle the LEDs on startup
    trellis_right.pixels[i] = PURPLE
    time.sleep(.05)

for i in range(16):
    trellis_right.pixels[i] = OFF
    time.sleep(.05)

#print(trellis.callbacks)
time.sleep(2)

while True:
    #call the sync function call any triggered callbacks
    trellis_left.sync()
    trellis_right.sync()
    #the trellis can only be read every 17 millisecons or so
    time.sleep(.02)
