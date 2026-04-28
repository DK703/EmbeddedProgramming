import paho.mqtt.client as mqtt
import numpy as np
import json
import time
import threading 
from threading import Event, Thread

# Challenge 2 - MQTT Thermal Controller with Auto/Request Modes

MQTT_BROKER = "broker.emqx.io"
TOPIC_PREFIX = "ECE140A"

REQUEST_TOPIC = f"{TOPIC_PREFIX}/request"
RESPONSE_TOPIC = f"{TOPIC_PREFIX}/response"
condition = Event()
#global response_count
response_count = 0
global boolAuto
boolAuto = True

#a separate function i set out a thread
def auto(client):
    print("auto should run")
    global response_count
    while not condition.is_set():
        response_count = response_count + 1
        print(f"Request {response_count} is sent")
        client.publish(REQUEST_TOPIC)                
        time.sleep(1)
        #boolAuto = False
        #input("s")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker with result code {reason_code}")
    client.subscribe(RESPONSE_TOPIC)


def on_message(client, userdata, msg):
    global response_count

    try:
        data = json.loads(msg.payload.decode())
        #prints out the thermistor data
        print("thermistor: ")
        print(data["thermistor"])
        print(" max: ")
        print(max(data["pixels"]))
        print(" min: ")
        print(min(data["pixels"]))
        print(f"Response {response_count} is recieved")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing response: {e}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    global response_count
    RunCommand = True
    global condition
    print(f"Connecting to {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_start()
    #this is needed so that way the if statement in
    #a has something to check.
    t1 = None

    time.sleep(1)
    print("For commands, press r to have one request response chain. \n")
    print("Press a to activate auto, and s to stop it \n")
    print("press q to quit")
    try:
        while RunCommand:
            
            userinput = input("")
            #i dont think user input interupts the mqtt, its rather my implentation

            if userinput == "r":
                #dont want r to be pressed while auto exist
                if t1 and t1.is_alive():
                    print("a was already pressed")
                else:
                    response_count = response_count + 1
                    print(f"Request {response_count} is sent")
                    client.publish(REQUEST_TOPIC, userinput)
            elif userinput == "a":
                #multiple auto's can be confusing
                if t1 and t1.is_alive():
                    print("a was already pressed")
                else:
                    condition.clear()
                    print("a was pressed")
                    #i need a separate thread so that way i can have a separate while loop 
                    #constatly running requesting and response while i can type anything
                    t1 = threading.Thread(target = auto, daemon = True, args=(client,))
                    t1.start()
                #need to add a while loop here, dont want it to end
            #to stop it    
            elif userinput == "s":
                print("s detected")
                condition.set()
            #make it quit
            elif userinput == "q":
                print("quit")
                client.loop_stop()
                client.disconnect()
                break
            else:
                print("Unknown input, please put the correct one")
            
    except KeyboardInterrupt:
        #client.publish(REQUEST_TOPIC, "dummy")
        print("\nExiting...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    main()
