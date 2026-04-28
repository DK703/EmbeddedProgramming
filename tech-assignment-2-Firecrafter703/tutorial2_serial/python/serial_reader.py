import serial
import serial.tools.list_ports
import json
import time

def find_esp32_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # this reflects our experience. In your machine your esp32 may be labeled differently
        # line 19 will print out all serial devices. If you see the right device replace line 15 with that string
        if "usb" in port.description or "ESP32" in port.description or "Feather" in port.description:
            return port.device
    return None

port = find_esp32_port()
if not port:
    print("No ESP32 found. Available ports:")
    for p in serial.tools.list_ports.comports():
        print(f"  {p.device} - {p.description}")
    exit(1)

print(f"Connecting to {port}...")
ser = serial.Serial(port, 115200, timeout=1)
time.sleep(2)

print("Reading from ESP32...")
while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        if line:
            data = json.loads(line)
            print(f"Button: {data['button']}")
