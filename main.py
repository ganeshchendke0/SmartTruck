# ============================
# MASTER CONTROLLER (FINAL)
# ============================
from machine import Pin
import time
import _thread
import sys

# ----------------------------
# POWER BUTTON
# ----------------------------
power_btn = Pin(23, Pin.IN, Pin.PULL_UP)

print("🔌 Power applied, system booting...")

# ----------------------------
# WAIT FOR POWER ON
# ----------------------------
while power_btn.value() == 1:
    time.sleep(0.1)

print("✅ Power button ON detected")

# ============================
# THREAD 1: MOTOR + BLE
# ============================
def start_motor():
    print("🚗 Starting motor & Bluetooth...")
    import truck_code_with_working   # has its own while True

# ============================
# THREAD 2: WEIGHT + THEFT
# ============================
def start_theft_system():
    print("⏳ Waiting 10 seconds before theft system...")
    time.sleep(10)

    print("📶 Connecting WiFi...")
    import wifi_connect
    wifi_connect.connect()

    print("⚖ Starting weight & theft detection...")
    import app   # has its own while True

# ============================
# START THREADS
# ============================
_thread.start_new_thread(start_motor, ())
_thread.start_new_thread(start_theft_system, ())

# ============================
# POWER OFF MONITOR
# ============================
while True:
    if power_btn.value() == 1:
        print("🔴 Power OFF detected")
        time.sleep(1)
        sys.exit()
    time.sleep(0.2)
