# Challenge 2: RGB LED Remote Control

## Description
Bidirectional MQTT communication where Python sends color commands to control the ESP32's NeoPixel LED.

## Setup
Add johboh/nlohmann-json@^3.12.0 to platformio.ini

### ESP32
1. Copy `esp32/env.example` to `esp32/.env`
2. Fill in your WiFi credentials and MQTT topic prefix
3. Upload to ESP32 using PlatformIO

### Python
```bash
cd python
uv run controller.py
```

## Commands
- `red` - Set LED to red
- `green` - Set LED to green
- `blue` - Set LED to blue
- `off` - Turn off LED
- `q` - Quit

## Example
```
LED Controller - Enter: red, green, blue, off (or q to quit)
> red
red is published
> blue
blue is published
```

## Video Demo
[\[YouTube Link Here\]](https://youtube.com/shorts/7UmqyeACnwI)
Note:renamed the csv file name to log.csv

## Github

https://github.com/UCSD-ECE140/tech-assignment-2-Firecrafter703