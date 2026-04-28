import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
import csv
from datetime import datetime

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "ECE140A" #was T1 before
CSV_FILE = "wifi_data.csv"


networks = {} # you should keep this json object filled with networks that are sent to python
connected_ssid = "" # this should be the wifi network you are connected to
connected_rssi = 0 # this should be the signal strength of the wifi network you are connected to

fig, ax = plt.subplots()

#with open(CSV_FILE, "w", newline="") as f:
    #writer = csv.writer(f)
    #writer.writerow(["timestamp", "connected_ssid", "connected_rssi", "network_count", "networks_json"]) # here is the header row for the csv
    #writer.writeheader()
    #writer.writerows(networks)

# our function to get color given a signal strength
def get_color(rssi):
    if rssi > -60:
        return 'green'
    elif rssi > -75:
        return 'orange'
    return 'red'

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker {rc}")
    client.subscribe(MQTT_TOPIC + "/signal")

def on_message(client, userdata, msg):
    global networks, connected_ssid, connected_rssi
    #data = json.loads(msg.payload.decode())
    #print("message is sent!")
    

    try:
        data = json.loads(msg.payload.decode())
        print(type(data))
        networks = data["network"]
        
        
        
        #got idea to sort values from geekstogeeks
        sort = {k: v for k, v in sorted(networks.items(), key=lambda item: item[1])}        

        i = 0

        #just print out top 3
        for x in reversed((sort)):
            if(i <= 2):
                print(x, sort[x])
            i = i + 1
        


        connected_ssid = data["connected_ssid"]
        connected_rssi = data["connected_rssi"]
        
        
    except Exception as e:
        print("Type of Exception:", type(e))
        print("Message:", e)
        print("")
        #print("exception, just straight up print the payload \n")
        #print(msg.payload.decode())

    # here you should set the ssid connected, rssi connected
    # update the networks such that given ssid key signal strength is the value
    # print to the CSV_FILE all columns required.

    #connected_ssid = "test"
    #connected_rssi = -10

    # you should also print out the top 3 strongest network signals
    #client.loop_forever()

    

def animate(frame):
    """
    Feel free to modify this function as you'd like
    This is our basic function to draw a bar chart given WIFI networks and strenghts
    """
    ax.clear()

    if not networks:
        ax.text(0.5, 0.5, "Waiting for data...", ha='center', va='center', fontsize=14)
        return

    #print("passed if statement!")
    sorted_nets = sorted(networks.items(), key=lambda x: x[1], reverse=True)
    #print(sorted_nets)
    ssids = [n[0] for n in sorted_nets]
    rssis = [n[1] for n in sorted_nets]
    colors = [get_color(r) for r in rssis]

    for i, ssid in enumerate(ssids):
        if ssid == connected_ssid:
            colors[i] = 'blue'

    bars = ax.barh(ssids, rssis, color=colors)
    ax.set_xlabel('RSSI (dBm)')
    ax.set_title(f'WiFi Networks | Connected: {connected_ssid} ({connected_rssi} dBm)')
    ax.set_xlim(-100, -20)

    ax.axvline(x=-60, color='green', linestyle='--', alpha=0.5, label='Excellent')
    ax.axvline(x=-75, color='orange', linestyle='--', alpha=0.5, label='Good')

    for bar, rssi in zip(bars, rssis):
        ax.text(rssi + 1, bar.get_y() + bar.get_height()/2, f'{rssi}', va='center', fontsize=8, color = "yellow")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

# here is our bar chat animation code. This will call animate every 1000 ms
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.tight_layout()
plt.show()

client.loop_stop()
#client.loop_forever()
