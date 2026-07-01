# SmartTruck

- 🏆 **Smart Truck Logistics Monitoring System (IoT)** — End-to-end cargo security system using ESP32, Load Cells, GPS & GSM modules with real-time alerts and live tracking. **Ranked 4th out of 65** in a competitive project exhibition.

SmartTruck combines real-time load monitoring, door status detection, GPS location reporting, Bluetooth motor control, and a Streamlit dashboard to help prevent theft and verify authorized unloading.

## Key Features

- Load cell integration with HX711 for cargo weight monitoring
- Door sensor monitoring to detect unauthorized access
- GPS position reporting via UART GPS module
- Owner-authorized unload command via ThingSpeak
- Motor control over Bluetooth for remote operation
- Streamlit dashboard for live status and theft alerts
- Wi-Fi connectivity support for ThingSpeak data exchange

## Repository Structure

- `main.py` - Master controller for ESP32 that starts the motor/BLE thread and the theft detection system.
- `app.py` - Theft detection and telemetry module for the ESP32; reads weight, door state, GPS, and sends data to ThingSpeak.
- `truck_code_with_working.py` - Motor and Bluetooth control logic for vehicle movement.
- `wifi_connect.py` - Wi-Fi connection helper for ESP32 devices.
- `hx711.py` - MicroPython HX711 load cell driver.
- `theft_dashboard/` - Streamlit dashboard application for monitoring truck telemetry.
- `theft_dashboard/config.py` - Dashboard configuration and environment variable support.
- `theft_dashboard/dashboard.py` - Streamlit UI and metrics display.

## Hardware Requirements

- ESP32 development board
- HX711 load cell amplifier
- Load cell sensor
- Door sensor (digital input)
- GPS module (UART)
- Buzzer
- Motor driver and motors for vehicle control
- Bluetooth-capable client for sending commands

## Setup Instructions

1. Install MicroPython on the ESP32.
2. Copy `main.py`, `app.py`, `truck_code_with_working.py`, `wifi_connect.py`, and `hx711.py` to the ESP32 filesystem.
3. Configure Wi-Fi credentials in `wifi_connect.py`.
4. Configure ThingSpeak API keys and channel IDs in `app.py`.
5. Adjust calibration and threshold values in `app.py` as needed:
   - `CALIBRATION_FACTOR`
   - `THEFT_THRESHOLD_G`
   - `BUZZER_TIME`
6. Wire the hardware according to the pin assignments in the code.

## Running the System

- Power the ESP32 and press the power button connected to `GPIO23`.
- The system will start the motor/BLE handler and theft detection module in separate threads.
- Use the button connected to `GPIO19` to begin loading and lock cargo weight.
- If unauthorized door access or weight removal is detected, the system can sound the buzzer and report events to ThingSpeak.

## Dashboard

To run the Streamlit dashboard:

```bash
cd theft_dashboard
python -m streamlit run dashboard.py
```

The dashboard reads telemetry from ThingSpeak and displays:

- Door status
- Weight and theft alerts
- GPS location data
- Owner unload command status

## Notes

- The current code uses ThingSpeak for telemetry and command exchange.
- `theft_dashboard/config.py` also supports environment variables for secure credentials.
- Update API keys and Wi-Fi credentials before deploying.
- This project is intended for prototype/demo use and may require customization for production.

