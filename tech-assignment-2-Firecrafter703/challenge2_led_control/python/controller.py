import paho.mqtt.client as mqtt
import csv
import json
import time
from datetime import datetime

MQTT_BROKER = "broker.emqx.io"
TOPIC_PREFIX = "ECE140A"
ProgramOn = True
CSV_FILE = "log.csv"
string = ""
bool = False



def on_connect(client, userdata, flags, rc):
    message = "ON"
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC_PREFIX+"/signal")
    #client.publish(TOPIC_PREFIX+"/command", message)
    #print("publish should run now...")
#
#i also write to the status file here. Note that it
#will be unable to have the status of the current csv 
def on_message(client, userdata, msg):
    print("message detected")
    
    try:
        data = json.loads(msg.payload.decode())
        #print("no exception \n")
        #print("Last state of the LED:")
        #print(f"data: {data}")
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            headername = ['color', 'rssi', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=headername)
            writer.writeheader()
            writer.writerow(data)
            
        
    except:
        #print("exception, just straight up print the payload \n")
        #print(msg.payload.decode())
        print('')

client = mqtt.Client()
#how to register callback
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.emqx.io", 1883, 60)
string = input("What is the led color you want:")

#print(userinput)

#this loop is needed so i can type commands on the input and have it be
#published to the esp32
while(ProgramOn):
    #userinput = input("what is led color you want:")
    print("at start of loop")
    client.loop_start()
    #time.sleep(5)
   
    print(string + " is published")
    client.publish(TOPIC_PREFIX+"/command", string)
    client.loop_stop()
    userinput = input("what is led color you want: ")
    #time.sleep(10)
    
    string = userinput
    if(string == "q"):
        break
    client.loop_stop()

    
    
#client.loop_start()
#userinput = input("What is the led color you want:")
#time.sleep(0.5)
#print(userinput)
#client.publish(TOPIC_PREFIX+"/command", userinput)
#client.loop_stop()