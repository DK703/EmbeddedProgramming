# Week 2: IoT Communication - MQTT & Serial

Learn how IoT devices communicate with applications using two key protocols: MQTT (wireless messaging) and Serial (USB communication). You'll send data from ESP32 to Python and control your board's RGB LED remotely.

## Prerequisites

### Installing uv (Python Package Manager)

We use `uv` for Python dependency management. Install it first:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, restart your terminal.

---

## Repository Structure

```
.
├── tutorial1_mqtt/          # Tutorial: MQTT Communication
│   ├── esp32/
│   │   ├── src/main.cpp
│   │   ├── include/
│   │   ├── platformio.ini
│   │   └── env.example
│   └── python/
│       ├── subscriber.py
│       └── pyproject.toml
│
├── tutorial2_serial/        # Tutorial: Serial Communication
│   ├── esp32/
│   │   ├── src/main.cpp
│   │   └── platformio.ini
│   └── python/
│       ├── serial_reader.py
│       └── pyproject.toml
│
├── challenge1_wifi_mapper/  # Challenge 1: WiFi Signal Mapper (50 pts)
│   ├── esp32/
│   │   ├── src/main.cpp
│   │   ├── include/
│   │   ├── platformio.ini
│   │   └── env.example
│   ├── python/
│   │   ├── visualizer.py
│   │   └── pyproject.toml
│   └── README.md
│
└── challenge2_led_control/  # Challenge 2: RGB LED Control (50 pts)
    ├── esp32/
    │   ├── src/main.cpp
    │   ├── include/
    │   ├── platformio.ini
    │   └── env.example
    ├── python/
    │   ├── controller.py
    │   └── pyproject.toml
    ├── log.csv
    └── README.md
```