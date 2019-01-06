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
``adafruit_neotrellism4``
====================================================

4x4 elastomer buttons and RGB LEDs

* Author(s): Dean Miller, Pierrick Couturier

Implementation Notes
--------------------

**Hardware:**

* Adafruit NeoTrellis M4 Express: https://www.adafruit.com/product/3938

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_neotrellis.git"

from time import sleep
import board
from adafruit_matrixkeypad import Matrix_Keypad
import digitalio
from neopixel import NeoPixel
from adafruit_seesaw.keypad import KeyEvent
from micropython import const

_NEO_TRELLIS_ADDR = const(0x2E)

_NEO_TRELLIS_NUM_ROWS = const(4)
_NEO_TRELLIS_NUM_COLS = const(4)
_NEO_TRELLIS_NUM_KEYS = const(16)

_NEO_TRELLIS_MAX_CALLBACKS = const(32)

_TRELLISM4_LEFT_PART = const(0)
_TRELLISM4_RIGHT_PART = const(4)

_EDGE_HIGH = const(0)
_EDGE_LOW = const(1)
_EDGE_FALLING = const(2)
_EDGE_RISING = const(3)

def _key(xval):
    return int(int(xval/4)*8 + (xval%4))

def _seesaw_key(xval):
    return int(int(xval/8)*4 + (xval%8))


class _TrellisNeoPixel:
    """Neopixel driver"""
    # Lots of stuff come from Adafruit_CircuitPython_seesaw/neopixel.py

    def __init__(self, pin, auto_write=True, brightness=1.0,
                 part=_TRELLISM4_LEFT_PART, left_part=None):
        if part == _TRELLISM4_LEFT_PART:
            self.pix = NeoPixel(pin, 32, auto_write=False, brightness=brightness)
        elif part == _TRELLISM4_RIGHT_PART:
            self.pix = left_part.pix
        self.auto_write = auto_write
        self._offset = part

    def __setitem__(self, key, color):
        self.pix[_key(key) + self._offset] = color
        if self.auto_write:
            self.show()

    def __getitem__(self, key):
        return self.pix[_key(key) + self._offset]

    def fill(self, color):
        """fill method wrapper"""
        # Suppress auto_write while filling.
        current_auto_write = self.auto_write
        self.auto_write = False
        for i in range(16):
            self[i] = color
        if current_auto_write:
            self.show()
        self.auto_write = current_auto_write

    def show(self):
        """fill method wrapper"""
        self.pix.show()


class _TrellisKeypad:
    """Simple Keypad object for Trellis M4
    No pixel, no rotation
    Key numbers : 0 - 15"""

    def __init__(self):
        col_pins = []
        #for x in range(8):
        for x in range(8):
            d = digitalio.DigitalInOut(getattr(board, "COL{}".format(x)))
            col_pins.append(d)

        row_pins = []
        for y in range(4):
            d = digitalio.DigitalInOut(getattr(board, "ROW{}".format(y)))
            row_pins.append(d)

        key_names = []
        for y in range(4):
            row = []
            for x in range(4):
                row.append(4*y+x)
            key_names.append(row)           # Keys of each halves is numbered from 0-15
        key_names = key_names + key_names   # so we need to double the names list

        self._matrix = Matrix_Keypad(col_pins, row_pins, key_names)

    @property
    def pressed_keys(self):
        """A list of tuples of currently pressed button coordinates.

        .. code-block:: python

            import time
            import adafruit_trellism4

            trellis = adafruit_trellism4.TrellisM4Express()

            current_press = set()
            while True:
                pressed = set(trellis.pressed_keys)
                for press in pressed - current_press:
                    print("Pressed:", press)
                for release in current_press - pressed:
                    print("Released:", release)
                time.sleep(0.08)
                current_press = pressed
        """
        return self._matrix.pressed_keys


class NeoTrellisM4:
    """Driver for the Adafruit NeoTrellis."""

    EDGE_HIGH = _EDGE_HIGH
    EDGE_LOW = _EDGE_LOW
    EDGE_FALLING = _EDGE_FALLING
    EDGE_RISING = _EDGE_RISING

    def __init__(self, left_part=None):
        if left_part is None:
            self._offset = _TRELLISM4_LEFT_PART
            self.pixels = _TrellisNeoPixel(board.NEOPIXEL)
            self.keypad = _TrellisKeypad()
        else:
            self._offset = _TRELLISM4_RIGHT_PART
            self.pixels = _TrellisNeoPixel(board.NEOPIXEL, 32,
                                           part=_TRELLISM4_RIGHT_PART,
                                           left_part=left_part.pixels)
            self.keypad = left_part.keypad

        self._events = [bytes()] * _NEO_TRELLIS_NUM_KEYS
        self._current_press = set()
        self._key_edges = [_EDGE_HIGH] * _NEO_TRELLIS_NUM_KEYS     # Keys edges
        self._current_events = bytearray()
        self.callbacks = [None] * 16

    @property
    def interrupt_enabled(self):
        """Only for compatibility with neotrellis module
        interrupts are disable on trellis M4 keypad"""
        return False

    # pylint: disable=unused-argument, no-self-use
    @interrupt_enabled.setter
    def interrupt_enabled(self, value):
        """Only for compatibility with neotrellis module
        interrupts are disable on trellis M4 keypad
        """

        print("Warning: no interrupt with Trellis M4 keypad (method does nothing)")
    # pylint: enable=unused-argument, no-self-use

    @property
    def count(self):
        """Return the pressed keys count ???
        """
        self._read_keypad()
        return len(self._current_events)

    # pylint: disable=unused-argument, no-self-use
    @count.setter
    def count(self, value):
        """Only for compatibility with neotrellis module"""
        raise AttributeError("count is read only")
    # pylint: enable=unused-argument, no-self-use

    def set_event(self, key, edge, enable):
        """Set event on a key:
        """
        if enable not in (True, False):
            raise ValueError("event enable must be True or False")
        if edge > 3 or edge < 0:
            raise ValueError("invalid edge")

        # Pas besoin de l'écriture sur I2C mais de l'enregistrer dans self._events
        self._events[key] = bytes((1 << (edge+1)) | enable)

        # Code original
        #cmd = bytearray(2)
        #cmd[0] = key
        #cmd[1] = (1 << (edge+1)) | enable

        #self.write(_KEYPAD_BASE, _KEYPAD_EVENT, cmd)

    def read_keypad(self, num):
        # Code original
        # ret = bytearray(num)
        # self.read(_KEYPAD_BASE, _KEYPAD_FIFO, ret)
        return self._current_events[:num]

    def _read_keypad(self):
        """Read keypad and update _key_edges and _current_events"""
        pressed = set(self.keypad.pressed_keys)
        print(pressed)
        #default : not pressed => EDGE_HIGH
        self._key_edges = [_EDGE_HIGH] * _NEO_TRELLIS_NUM_KEYS
        for k in pressed:
            self._key_edges[k] = _EDGE_LOW
        for k in pressed - self._current_press:
            self._key_edges[k] = _EDGE_FALLING
        for k in self._current_press - pressed:
            self._key_edges[k] = _EDGE_RISING

    def activate_key(self, key, edge, enable=True):
        """Activate or deactivate a key on the trellis. Key is the key number from
           0 to 15. Edge specifies what edge to register an event on and can be
           NeoTrellis.EDGE_FALLING or NeoTrellis.EDGE_RISING. enable should be set
           to True if the event is to be enabled, or False if the event is to be
           disabled."""
        self.set_event(key, edge, enable)

    def sync(self):
        """Read any events from the Trellis hardware and call associated
           callbacks"""
        available = self.count
        sleep(.0005)
        if available > 0:
            available = available + 2
            buf = self.read_keypad(available)
            for raw in buf:
                evt = KeyEvent(_seesaw_key((raw >> 2) & 0x3F), raw & 0x3)
                if evt.number < _NEO_TRELLIS_NUM_KEYS and self.callbacks[evt.number] is not None:
                    self.callbacks[evt.number](evt)
