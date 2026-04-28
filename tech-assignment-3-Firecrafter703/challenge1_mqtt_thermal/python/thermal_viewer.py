import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import json
import csv
from datetime import datetime

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC =   "ece140a"
CSV_FILE = "thermal_data.csv"

# Initialize thermal data storage
thermal_data = np.zeros((8, 8))
thermistor_temp = 0.0

fig, ax = plt.subplots()
im = ax.imshow(thermal_data, cmap='inferno', vmin=15, vmax=40)
cbar = plt.colorbar(im, ax=ax, label='Temperature (C)')
ax.set_title('AMG8833 Thermal Camera (MQTT)')

# Initialize CSV file. Appending is done in the subscribe.
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "thermistor", "max_temp", "min_temp"])
    #writer.writerow(["timestamp", "thermistor"])

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC + "/thermal")
    print(f"Subscribed to topic: {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    global thermal_data, thermistor_temp
    # do something here
    #print("message")
    try:
        data = json.loads(msg.payload.decode())
        #print("thermistor: ")
        #print(data["thermistor"])
        #print("\n pixels: ")
        #print(data["pixels"])
        thermal_data = np.array(data['pixels']).reshape(8, 8)
        thermistor_temp = data["thermistor"]
        current_datetime = datetime.now()
        timestamp = current_datetime.timestamp()
        #print("\n max: ")
        #print(max(data["pixels"]))
        #print("\ min: ")
        #print(min(data["pixels"]))
        #appends it to thermal data csv. Separate from the one that opens it above 
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([str(timestamp),str(thermistor_temp),max(data["pixels"]),min(data["pixels"])])


        
    except Exception as e:
        print("Type of Exception:", type(e))
        print("Message:", e)
        print("fefefe")

def animate(frame):
    global thermal_data, thermistor_temp
    

    if thermal_data.max() > 0:
        im.set_array(thermal_data)

        # Auto-adjust color scale
        vmin = thermal_data.min() - 2
        vmax = thermal_data.max() + 2
        im.set_clim(vmin, vmax)

        ax.set_title(f'AMG8833 Thermal Camera | Ambient: {thermistor_temp:.1f}C | Max: {thermal_data.max():.1f}C')

    return [im]

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

# Run animation
ani = animation.FuncAnimation(fig, animate, interval=100, blit=True)
plt.tight_layout()
plt.show()

client.loop_stop()
