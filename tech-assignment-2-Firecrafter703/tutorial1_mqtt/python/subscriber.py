import paho.mqtt.client as mqtt
import json
import time
TOPIC_PREFIX = "ECE140A"
# this needs to match the topic prefix in the main.cpp
ready= False
#function that define callback
def on_connect(client, userdata, flags, rc):
    global ready
    ready = True
    message = "ON"
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC_PREFIX+"/signal")
    client.publish(TOPIC_PREFIX+"/command", message)
    print("publish should run now...")
#telling MQtt what we want to do when a message comes in
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("no exception \n")
        print(f"Device: {data['device']}, Signal: {data['rssi']} dBm, data: {data}")
    except:
        print("exception, just straight up print the payload \n")
        print(msg.payload.decode())
message = "ON"
#how to register callback
client = mqtt.Client()
#how to register callback
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.emqx.io", 1883, 60)
print(ready)
#while not ready:
    #time.sleep(0.1)
#for i in range(3):
    #print(ready)

#client.publish(TOPIC_PREFIX+"/command", message)
#print("sent")
#infinte loop important for sending message (ONLY LOOPS AT THIS LINE + 1)
client.loop_forever()

