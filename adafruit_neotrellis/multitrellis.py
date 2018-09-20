# The MIT License (MIT)
#
# Copyright (c) 2018 Dean Miller for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
interface for connecting together multiple NeoTrellis boards.
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_neotrellis.git"

from time import sleep
from adafruit_seesaw.keypad import KeyEvent
from micropython import const

_NEO_TRELLIS_NUM_KEYS = const(16)

def _key(xval):
    return int(int(xval/4)*8 + (xval%4))

def _seesaw_key(xval):
    return int(int(xval/8)*4 + (xval%8))

class MultiTrellis(object):
    """Driver for multiple connected Adafruit NeoTrellis boards."""
    def __init__(self, neotrellis_array):
        self._trelli = neotrellis_array
        self._rows = len(neotrellis_array)
        self._cols = len(neotrellis_array[0])

    def activate_key(self, x, y, edge, enable=True):
        """Activate or deactivate a key on the trellis. x and y are the index
        of the key measured from the top lefthand corner. Edge specifies what
        edge to register an event on and can be NeoTrellis.EDGE_FALLING or
        NeoTrellis.EDGE_RISING. enable should be set to True if the event is
        to be enabled, or False if the event is to be disabled."""
        xkey = x%4
        ykey = int(int(y%4)*4/4)
        self._trelli[int(y/4)][int(x/4)].activate_key(ykey*4 + xkey, edge, enable)

    def set_callback(self, x, y, function):
        """Set a callback function for when an event for the key at index x, y
        (measured from the top lefthand corner) is detected."""
        xkey = x%4
        ykey = int(int(y%4)*4/4)
        self._trelli[int(y/4)][int(x/4)].callbacks[ykey*4 + xkey] = function

    def color(self, x, y, color):
        """Set the color of the pixel at index x, y measured from the top
        lefthand corner of the matrix"""
        xkey = x%4
        ykey = int(int(y%4)*4/4)
        self._trelli[int(y/4)][int(x/4)].pixels[ykey*4 + xkey] = color

    def sync(self):
        """Read all trellis boards in the matrix and call any callbacks"""
        for _n in range(self._rows):
            for _m in range(self._cols):

                _t = self._trelli[_n][_m]
                available = _t.count
                sleep(.0005)
                if available > 0:
                    available = available + 2
                    buf = _t.read_keypad(available)
                    for raw in buf:
                        evt = KeyEvent(_seesaw_key((raw >> 2) & 0x3F), raw & 0x3)
                        if evt.number < _NEO_TRELLIS_NUM_KEYS \
                           and _t.callbacks[evt.number] is not None:
                            y = int(evt.number/4)+_n*4
                            x = int(evt.number%4)+_m*4
                            _t.callbacks[evt.number](x, y, evt.edge)
