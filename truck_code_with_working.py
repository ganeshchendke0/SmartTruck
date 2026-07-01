from machine import Pin, PWM
import bluetooth
import time

# ================= MOTOR PIN CONNECTION =================
# L298N -> ESP32
# IN1 -> GPIO19
# IN2 -> GPIO18
# IN3 -> GPIO5
# IN4 -> GPIO17
# ENA -> GPIO25
# ENB -> GPIO26

IN1 = Pin(13, Pin.OUT) 
IN2 = Pin(14, Pin.OUT)
IN3 = Pin(32, Pin.OUT)
IN4 = Pin(17, Pin.OUT)

ENA = PWM(Pin(25), freq=1500)
ENB = PWM(Pin(33), freq=1500)

ENA.duty(0)
ENB.duty(0)

# ================= MOTOR FUNCTIONS =================
def stop():
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.off()
    ENA.duty(0)
    ENB.duty(0)
    print("STOP")

def forward(speed):
    IN1.off()
    IN2.on()
    IN3.off()
    IN4.on()
    ENA.duty(speed)
    ENB.duty(speed)
    print("FORWARD", speed)

def backward(speed):
    IN1.on()
    IN2.off()
    IN3.on()
    IN4.off()
    ENA.duty(speed)
    ENB.duty(speed)
    print("BACKWARD", speed)

def left(speed):
    IN1.off()
    IN2.on()
    IN3.off()
    IN4.off()
    ENA.duty(speed)
    ENB.duty(speed)
    print("LEFT", speed)

def right(speed):
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.on()
    ENA.duty(speed)
    ENB.duty(speed)
    print("RIGHT", speed)

stop()

# ================= BLE SETUP =================
ble = bluetooth.BLE()
ble.active(True)

UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
TX_UUID   = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
RX_UUID   = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")

UART_SERVICE = (
    UART_UUID,
    (
        (TX_UUID, bluetooth.FLAG_NOTIFY),
        (RX_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE),
    ),
)

((tx_handle, rx_handle),) = ble.gatts_register_services((UART_SERVICE,))

# ================= BLE HANDLER =================
def bt_irq(event, data):
    if event == 1:
        print("Bluetooth Connected")

    elif event == 2:
        print("Bluetooth Disconnected")
        stop()
        advertise()

    elif event == 3:
        _, handle = data
        if handle == rx_handle:
            msg = ble.gatts_read(rx_handle).decode().strip()
            print("RX:", msg)

            if msg == "S":
                stop()
                return

            try:
                direction, speed = msg.split(":")
                speed = int(speed)
                speed = max(0, min(speed, 255))
                speed = int(speed * 1023 / 255)  # 🔥 PWM FIX
            except:
                stop()
                return

            if direction == "B":
                forward(speed)
            elif direction == "F":
                backward(speed)
            elif direction == "L":
                left(speed)
            elif direction == "R":
                right(speed)
            else:
                stop()

ble.irq(bt_irq)

# ================= ADVERTISING =================
def advertise():
    name = b"ROLLS ROYCE"
    payload = b"\x02\x01\x06" + bytes((len(name)+1, 0x09)) + name
    ble.gap_advertise(100_000, payload)
    print("Advertising as ROLLS ROYCE")

advertise()

# ================= MAIN LOOP =================
while True:
    time.sleep(1)
