# Challenge 2: MQTT Request-Response Thermal Camera

## Description
Implement a request-response pattern where Python requests thermal data and ESP32 responds immediately. **NO DELAYS ALLOWED** in the ESP32 loop - the device must be responsive at all times.

## Setup

### ESP32
1. Copy `esp32/env.example` to `esp32/.env`
2. Fill in your WiFi credentials
3. Set your unique `CLIENT_ID` and `TOPIC_PREFIX` in `main.cpp`
4. Upload to ESP32 using PlatformIO

### Python
```bash
cd python
uv run thermal_controller.py
```

Make sure `TOPIC_PREFIX` in `thermal_controller.py` matches your ESP32 `TOPIC_PREFIX`.

## MQTT Topics
- **Request Topic**: `{TOPIC_PREFIX}/request` - Python sends requests here
- **Response Topic**: `{TOPIC_PREFIX}/response` - ESP32 publishes responses here

## Commands (in Python terminal)
- `r` - Send single request for thermal data
- `a` - Start auto-request mode (every 1 second)
- `s` - Stop auto-request mode
- `q` - Quit

## Key Requirements
1. **NO delay() in loop()** - The ESP32 must respond immediately when a request arrives
2. Use a flag-based approach: callback sets a flag, loop checks and responds
3. ESP32 subscribes to request topic, publishes to response topic
4. Python controls when data is sent (pull model vs push model)

## Example Interaction
```
Connected to MQTT broker with result code 0
Subscribed to response topic: ece140a/response
Will send requests to: ece140a/request

Commands:
  r - Request thermal data
  a - Start auto-request (every 1 second)
  s - Stop auto-request
  q - Quit

r
Request 1 is sent
Ambient:25.5C
Max:32.1C
Min:24.2C
Request 1 is received
a
auto should run
Request 2 is sent
Ambient:25.5C
Max:33.0C
Min:24.1C
Request 2 is recieved
Request 3 is sent
Request 3 is recievedSent request for thermal data
Ambient:25.6C
Max:32.8C
Min:24.3C
s detected
q

```

## Video Demo
[(https://www.youtube.com/shorts/S7_aiV9b8FA)]
