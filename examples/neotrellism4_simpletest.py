import time

import board
import busio
from adafruit_neotrellis.neotrellism4 import NeoTrellisM4, TrellisNeoPixel


#create the trellis
np = TrellisNeoPixel(board.NEOPIXEL)
trellis = NeoTrellisM4(np)

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
        trellis.pixels[event.number] = CYAN
    #turn the LED off when a rising edge is detected
    elif event.edge == NeoTrellisM4.EDGE_FALLING:
        trellis.pixels[event.number] = OFF

for i in range(16):
    #activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellisM4.EDGE_RISING)
    #activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellisM4.EDGE_FALLING)
    #set all keys to trigger the blink callback
    trellis.callbacks[i] = blink

    #cycle the LEDs on startup
    trellis.pixels[i] = PURPLE
    time.sleep(.05)

for i in range(16):
    trellis.pixels[i] = OFF
    time.sleep(.05)

while True:
    #call the sync function call any triggered callbacks
    trellis.sync()
    #the trellis can only be read every 17 millisecons or so
    time.sleep(.02)
