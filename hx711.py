"""
MicroPython HX711 driver (Stable Version)
Compatible with ESP32 + load cell
Supports tare(), set_scale(), get_units()
"""

from machine import Pin
from time import sleep_us, sleep


class HX711:
    def __init__(self, dt, sck, gain=128):
        # Pins
        self.dt = Pin(dt, Pin.IN)
        self.sck = Pin(sck, Pin.OUT)
        self.sck.value(0)

        # Calibration
        self.offset = 0
        self.scale = 1

        # Gain setup
        if gain == 128:
            self.gain_pulses = 1
        elif gain == 64:
            self.gain_pulses = 3
        elif gain == 32:
            self.gain_pulses = 2
        else:
            raise ValueError("Gain must be 128, 64, or 32")

        # Let HX711 settle
        sleep(0.1)

    # -----------------------------
    # Check if HX711 is ready
    # -----------------------------
    def is_ready(self):
        return self.dt.value() == 0

    # -----------------------------
    # Read raw 24-bit value
    # -----------------------------
    def read_raw(self):
        while not self.is_ready():
            pass

        count = 0
        for _ in range(24):
            self.sck.value(1)
            sleep_us(1)
            count = (count << 1) | self.dt.value()
            self.sck.value(0)
            sleep_us(1)

        # Set gain for next reading
        for _ in range(self.gain_pulses):
            self.sck.value(1)
            sleep_us(1)
            self.sck.value(0)
            sleep_us(1)

        # Convert from 24-bit two's complement
        if count & 0x800000:
            count |= ~0xffffff

        return count

    # -----------------------------
    # Average multiple readings
    # -----------------------------
    def read_average(self, times=10):
        total = 0
        for _ in range(times):
            total += self.read_raw()
        return total // times

    # -----------------------------
    # Tare (zero the scale)
    # -----------------------------
    def tare(self, times=15):
        self.offset = self.read_average(times)
        return self.offset

    # -----------------------------
    # Set calibration factor
    # -----------------------------
    def set_scale(self, scale):
        self.scale = scale

    # -----------------------------
    # Read value (raw - offset)
    # -----------------------------
    def get_value(self, times=10):
        return self.read_average(times) - self.offset

    # -----------------------------
    # Read weight in units (grams)
    # -----------------------------
    def get_units(self, times=10):
        value = self.get_value(times) / self.scale
        return value
