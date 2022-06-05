# SPDX-FileCopyrightText: 2021 Dean Miller for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
``adafruit_multitrellis``
====================================================

A CircuitPython driver class for interfacing clusters of 4x4 NeoTrellis with
elastomer buttons and NeoPixel RGB LEDs.

* Author(s): Dean Miller, JG for CedarGroveMakerStudios

Implementation Notes
--------------------

**Hardware:**

* 'NeoTrellis RGB Driver PCB for 4x4 Keypad, PID: 3954
  <https://www.adafruit.com/product/3954>'

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit Seesaw CircuitPython library
  https://github.com/adafruit/Adafruit_CircuitPython_seesaw/releases
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_neotrellis.git"


from time import sleep
from micropython import const
from adafruit_seesaw.keypad import KeyEvent

_NEO_TRELLIS_NUM_KEYS = const(16)


def _key(xval):
    return int(int(xval / 4) * 8 + (xval % 4))


def _seesaw_key(xval):
    return int(int(xval / 8) * 4 + (xval % 8))


class MultiTrellis:
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
        xkey = x % 4
        ykey = int(int(y % 4) * 4 / 4)
        self._trelli[int(y / 4)][int(x / 4)].activate_key(ykey * 4 + xkey, edge, enable)

    def set_callback(self, x, y, function):
        """Set a callback function for when an event for the key at index x, y
        (measured from the top lefthand corner) is detected."""
        xkey = x % 4
        ykey = int(int(y % 4) * 4 / 4)
        self._trelli[int(y / 4)][int(x / 4)].callbacks[ykey * 4 + xkey] = function

    def color(self, x, y, color):
        """Set the color of the pixel at index x, y measured from the top
        lefthand corner of the matrix"""
        xkey = x % 4
        ykey = int(int(y % 4) * 4 / 4)
        self._trelli[int(y / 4)][int(x / 4)].pixels[ykey * 4 + xkey] = color

    def sync(self):
        """Read all trellis boards in the matrix and call any callbacks"""
        for _n in range(self._rows):
            for _m in range(self._cols):

                _t = self._trelli[_n][_m]
                available = _t.count
                sleep(0.0005)
                if available > 0:
                    available = available + 2
                    buf = _t.read_keypad(available)
                    for raw in buf:
                        evt = KeyEvent(_seesaw_key((raw >> 2) & 0x3F), raw & 0x3)
                        if (
                            evt.number < _NEO_TRELLIS_NUM_KEYS
                            and _t.callbacks[evt.number] is not None
                        ):
                            y = int(evt.number / 4) + _n * 4
                            x = int(evt.number % 4) + _m * 4
                            _t.callbacks[evt.number](x, y, evt.edge)

    @property
    def brightness(self):
        """The NeoPixel brightness level of all clustered NeoTrellis boards."""
        return self._brightness

    @brightness.setter
    def brightness(self, new_brightness):
        """Select a NeoPixel brightness level for all all clustered boards. A
        valid brightness value is in the range of 0.0 to 1.0."""
        self._brightness = new_brightness
        for _r in range(self._rows):
            for _c in range(self._cols):
                self._trelli[_r][_c].brightness = self._brightness
