# SPDX-FileCopyrightText: 2021 Dean Miller for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
``adafruit_neotrellis``
====================================================

A CircuitPython driver class for the 4x4 NeoTrellis with elastomer buttons and
NeoPixel RGB LEDs.

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
from adafruit_seesaw.keypad import Keypad, KeyEvent
from adafruit_seesaw.neopixel import NeoPixel, GRB

_NEO_TRELLIS_ADDR = const(0x2E)

_NEO_TRELLIS_NEOPIX_PIN = const(3)

_NEO_TRELLIS_NUM_ROWS = const(4)
_NEO_TRELLIS_NUM_COLS = const(4)
_NEO_TRELLIS_NUM_KEYS = const(16)

_NEO_TRELLIS_MAX_CALLBACKS = const(32)


def _key(xval):
    return int(int(xval / 4) * 8 + (xval % 4))


def _seesaw_key(xval):
    return int(int(xval / 8) * 4 + (xval % 8))


# pylint: disable=too-many-arguments
class NeoTrellis(Keypad):
    """Driver for the Adafruit 4x4 NeoTrellis."""

    def __init__(
        self,
        i2c_bus,
        interrupt=False,
        addr=_NEO_TRELLIS_ADDR,
        drdy=None,
        brightness=1.0,
    ):
        super().__init__(i2c_bus, addr, drdy)
        self.interrupt_enabled = interrupt
        self._brightness = brightness
        self.callbacks = [None] * _NEO_TRELLIS_NUM_KEYS
        self.pixels = NeoPixel(
            self,
            _NEO_TRELLIS_NEOPIX_PIN,
            _NEO_TRELLIS_NUM_KEYS,
            brightness=self._brightness,
            pixel_order=GRB,
        )

    def activate_key(self, key, edge, enable=True):
        """Activate or deactivate a key on the trellis. Key is the key number from
        0 to 16. Edge specifies what edge to register an event on and can be
        NeoTrellis.EDGE_FALLING or NeoTrellis.EDGE_RISING. enable should be set
        to True if the event is to be enabled, or False if the event is to be
        disabled."""
        self.set_event(_key(key), edge, enable)

    def sync(self):
        """read any events from the Trellis hardware and call associated
        callbacks"""
        available = self.count
        sleep(0.0005)
        if available > 0:
            available = available + 2
            buf = self.read_keypad(available)
            for raw in buf:
                evt = KeyEvent(_seesaw_key((raw >> 2) & 0x3F), raw & 0x3)
                if (
                    evt.number < _NEO_TRELLIS_NUM_KEYS
                    and self.callbacks[evt.number] is not None
                ):
                    self.callbacks[evt.number](evt)

    @property
    def brightness(self):
        """The NeoPixel brightness level of the board."""
        return self._brightness

    @brightness.setter
    def brightness(self, new_brightness):
        """Select a NeoPixel brightness level for the board. A valid brightness
        value is in the range of 0.0 to 1.0."""
        self._brightness = new_brightness
        self.pixels.brightness = self._brightness
