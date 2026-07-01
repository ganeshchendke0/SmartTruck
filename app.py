from machine import Pin, UART
import time
import urequests
#import wifi_connect
from hx711 import HX711

# ============================
# WIFI
# ============================
#wifi_connect.connect()

# ============================
# THINGSPEAK
# ============================
WRITE_API_KEY = "Z0TT1DCL1DUH6A5P"
READ_API_KEY  = "76UI1H11CWP4O4DU"
CHANNEL_ID    = "3234262"

WRITE_URL = "http://api.thingspeak.com/update"
READ_URL  = "http://api.thingspeak.com/channels/{}/fields/7/last.json?api_key={}".format(
    CHANNEL_ID, READ_API_KEY
)

TRUCK_ID = "TRUCK_01"

# ============================
# PINS
# ============================
door   = Pin(15, Pin.IN, Pin.PULL_UP)
button = Pin(19, Pin.IN, Pin.PULL_UP)
buzzer = Pin(18, Pin.OUT)
hx     = HX711(4, 5)
gps    = UART(2, baudrate=9600, rx=26, tx=27)

buzzer.value(0)

# ============================
# SETTINGS (GRAMS)
# ============================
CALIBRATION_FACTOR = 489
THEFT_THRESHOLD_G = 20
BUZZER_TIME = 5

locked_weight = None
loading = False
journey_active = False
owner_unload_allowed = False

# ============================
# HX711 SETUP
# ============================
print("Taring... remove all load")
time.sleep(2)
hx.tare()
hx.set_scale(CALIBRATION_FACTOR)
print("Tare done")

# ============================
# READ WEIGHT (GRAMS)
# ============================
def read_weight_g(samples=10):
    total = 0
    for _ in range(samples):
        total += abs(hx.get_units(1))
        time.sleep(0.05)
    avg = total / samples
    if avg < 5:
        avg = 0
    return round(avg, 1)

# ============================
# LOCK WEIGHT (10th READING)
# ============================
def lock_weight_10th():
    print("🔒 Locking load (10 readings)...")
    last = 0
    for i in range(10):
        last = read_weight_g()
        print(f"   Reading {i+1}: {last} g")
        time.sleep(0.5)
    print("🔐 LOCKED:", last, "g")
    return last

# ============================
# GPS READ
# ============================
def read_gps(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        if gps.any():
            line = gps.readline()
            if line and b"GPGGA" in line:
                try:
                    d = line.decode().split(",")
                    if d[6] != "0":
                        lat = int(float(d[2]) / 100) + (float(d[2]) % 100) / 60
                        lon = int(float(d[4]) / 100) + (float(d[4]) % 100) / 60
                        return round(lat, 6), round(lon, 6)
                except:
                    pass
    return "0", "0"

# ============================
# OWNER COMMAND
# ============================
last_owner_command = "0"
owner_unload_allowed = False

def read_owner_command():
    global owner_unload_allowed, last_owner_command
    try:
        r = urequests.get(READ_URL)
        data = r.json()
        r.close()

        current_cmd = str(data.get("field7", "0"))

        # 🔥 Detect rising edge (0 → 1)
        if current_cmd == "1" and last_owner_command == "0":
            owner_unload_allowed = True
            print("📩 NEW OWNER UNLOAD COMMAND RECEIVED")

        last_owner_command = current_cmd

    except Exception as e:
        print("❌ Owner command read error:", e)


# ============================
# BUZZER
# ============================
def buzzer_beep():
    buzzer.value(1)
    time.sleep(BUZZER_TIME)
    buzzer.value(0)

# ============================
# SEND TO THINGSPEAK
# ============================
def send_ts(door, weight, theft, lat="0", lon="0"):
    link = (
        WRITE_URL +
        "?api_key=" + WRITE_API_KEY +
        "&field1=" + str(door) +
        "&field2=" + str(weight) +
        "&field3=" + str(theft) +
        "&field4=" + TRUCK_ID +
        "&field5=" + str(lat) +
        "&field6=" + str(lon)
    )
    try:
        r = urequests.get(link)
        r.close()
        print("📡 Sent → Door:", door,
              "Weight:", weight,
              "Theft:", theft,
              "Lat:", lat,
              "Lon:", lon)
    except:
        print("❌ ThingSpeak error")

# ============================
# MAIN LOOP
# ============================
# ============================
# INITIAL SYNC WITH OWNER COMMAND (IMPORTANT)
# ============================
try:
    r = urequests.get(READ_URL)
    data = r.json()
    r.close()
    last_owner_command = str(data.get("field7", "0"))
    print("🔄 Owner command synced at boot:", last_owner_command)
except:
    last_owner_command = "0"


print("System started")
prev_door = door.value()

while True:
    read_owner_command()
    door_status = door.value()
    button_state = button.value()

    # DRIVER LOADING (ONLY BEFORE JOURNEY)
    if button_state == 0 and not journey_active:
        loading = True
        locked_weight = None
        print("🔄 Driver loading...")
        time.sleep(0.5)
        continue

    # LOCK & START JOURNEY
    if loading and button_state == 1:
        locked_weight = lock_weight_10th()
        send_ts(door_status, locked_weight, 0)
        loading = False
        journey_active = True
        print("🚚 Journey started")

    # DOOR OPEN → CHECK THEFT
    if prev_door == 0 and door_status == 1 and locked_weight is not None:
        print("🚪 Door opened")
        buzzer_beep()

        current_weight = read_weight_g(10)
        diff = locked_weight - current_weight

        theft = 0
        lat = "0"
        lon = "0"

        if diff >= THEFT_THRESHOLD_G:
            if not owner_unload_allowed:
                theft = 1
                lat, lon = read_gps()

                print("🚨🚨 THEFT DETECTED 🚨🚨")
                print("📍 GPS Location → Lat:", lat, "Lon:", lon)
            else:
                print("✅ Authorized unloading by owner")

        send_ts(door_status, current_weight, theft, lat, lon)

        # RESET AFTER AUTHORIZED UNLOAD
        if owner_unload_allowed:
            print("♻ System reset for next trip")
            locked_weight = None
            journey_active = False
            owner_unload_allowed = False

    prev_door = door_status
    time.sleep(2)
