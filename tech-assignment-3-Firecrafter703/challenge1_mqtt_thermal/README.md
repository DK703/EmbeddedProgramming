# Challenge 1: MQTT Thermal Camera

## Description
Send AMG8833 thermal camera data over MQTT and visualize it in real-time with Python. Delays are allowed in this challenge.

## Setup
lib_deps = knolleary/PubSubClient and adafruit/Adafruit AMG88xx Library
Imports for Python:paho.mqtt.client,matplotlib.pyplot,
matplotlib.animation, numpy, json, csv, datetime
Imports for ESP32: Arduino.h, WiFi.h, Wire.h, Adafruit_AMG88xx.h, ECE140_WIFI.h, ECE140_MQTT.h
### ESP32
1. Copy `esp32/env.example` to `esp32/.env`
2. Fill in your WiFi credentials
3. Set your unique `CLIENT_ID` and `TOPIC_PREFIX` in `main.cpp`
4. Upload to ESP32 using PlatformIO

### Python
```bash
cd python
uv run thermal_viewer.py
```

Make sure `MQTT_TOPIC` in `thermal_viewer.py` matches your `TOPIC_PREFIX + "/thermal"`.

## Features
- Read 8x8 thermal array (64 temperature values)
- Publish data as JSON over MQTT every second
- Real-time heatmap visualization
- Color scale: inferno (purple = cold, yellow = hot)
- Data logging to `thermal_data.csv`

## JSON Format
```json
{
  "thermistor": 25.5,
  "pixels": [24.5, 25.0, 25.5, ... (64 values)]
}
```

## Example Output
```
Connected to MQTT broker with result code 0
Subscribed to topic: ece140a/thermal/thermal
Received: Ambient=25.5C | Max=32.1C | Min=24.2C
Received: Ambient=25.5C | Max=35.8C | Min=24.1C
```

## Video Demo
[https://youtube.com/shorts/7TLYxL3GVBI?feature=share]
