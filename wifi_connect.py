import network
import time

SSID = "Ganu"
PASSWORD = "12345678"

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        time.sleep(1)

    print("WiFi Connected")
    print("IP:", wlan.ifconfig()[0])
    

