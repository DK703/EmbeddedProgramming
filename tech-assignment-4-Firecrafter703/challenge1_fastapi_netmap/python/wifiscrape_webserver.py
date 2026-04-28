import os
import io
import json
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse, StreamingResponse # for returning an image, StreamingResponse is used to return a stream of bytes, typically performs better than returning a file object
from pydantic import BaseModel, Field, ValidationError

from visualize import generate_netmap_plot

load_dotenv("../esp32/.env")
# TODO: Fill out the environment variables from the .env file
MQTT_BROKER = os.getenv("MQTT_BROKER") # MQTT broker address
MQTT_BROKER_PORT = 1883 
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_COMMAND_TOPIC = f"{MQTT_TOPIC}/command" # Remember, we need to subscribe to this topic on the ESP32 side!
MQTT_SCAN_TOPIC = f"{MQTT_TOPIC}/scan" # Remember, we need to publish to this topic on the ESP32 side!

###################################################################################
########## DO NOT CHANGE THE CODE BETWEEN THESE LINES #############################
###################################################################################
# Pydantic validation models
# Look inside these validation models to understand the structure of the data that
# we are expecting from the ESP32. It is on you to that the data is correctly 
# formatted.
class Network(BaseModel):
    """Model for individual WiFi network"""
    ssid: str = Field(..., description="Network SSID name")
    rssi: int = Field(..., description="Signal strength (RSSI value)")

class ScanResult(BaseModel):
    """Model for complete WiFi scan result from ESP32"""
    device_id: str = Field(..., description="ESP32 device identifier")
    connected_ssid: str = Field(..., description="Currently connected network SSID")
    connected_rssi: int = Field(..., description="Signal strength of connected network")
    networks: list[Network] = Field(..., description="List of detected WiFi networks")

###################################################################################
########## DO NOT CHANGE THE CODE BETWEEN THESE LINES #############################
###################################################################################


# Global variables for storing scan data
##############################################################
##### Inside of any function, you MUST use the `global` ######
##### keyword to access the global variables.           ######
###############################################################
global scan_result 
scan_result = None


# This is completely optional. If you don't want to use it, you can remove it.
# The intention is to be able to keep track of whether or not we got a fresh
# scan result or not.
global previous_scan_result #OPTIONAL TO USE!
previous_scan_result = None #OPTIONAL TO USE!


# MQTT callbacks
# TODO: Implement the on_connect function

#command set
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_SCAN_TOPIC)



# This time we were nice and provided you with the on_message function.
# Due to the nature of callbacks, we cannot return the result directly into
# the api endpoint function. Instead we store the result in the global
# variable named scan_result.
def on_message(client, userdata, msg):
    global scan_result
    global previous_scan_result
    print("there was a message")
    #print(msg)
    #print(msg.payload)
    data = msg.payload.decode()
    #print("[Received MQTT message]")
    #print(data)
    #print(json.loads(data))
    
    try:
        # Parse JSON data
        json_data = json.loads(data)
        print(json_data)
        
        # Validate against Pydantic model
        validated_data = ScanResult(**json_data)
        
        if scan_result:
            scan_result = validated_data.model_dump_json()

        else:
        # Store validated data as JSON string
            previous_scan_result = scan_result
            scan_result = validated_data.model_dump_json()
        print(f"[Validation Success] Data validated and stored in `scan_result` global variable")   
    except json.JSONDecodeError as e:
        print(f"[Validation Error] Invalid JSON format: {e}")
    except ValidationError as e:
        print(f"[Validation Error] Data does not match required format:")
        print(e)

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect # <- Don't forget to implement the on_connect function!
mqtt_client.on_message = on_message


# We discussed this durint the lab session. This is the correct way to initialize
# the MQTT client and start the client loop. Such that we gracefully shutdown the
# client when the server is stopped.
@asynccontextmanager
async def lifespan(app: FastAPI):
    if MQTT_BROKER:
        mqtt_client.connect(MQTT_BROKER, MQTT_BROKER_PORT, 60)
        mqtt_client.loop_start()
        print(f"MQTT client started, connecting to {MQTT_BROKER}")
    else:
        print("Warning: MQTT_BROKER not configured")

    yield 
    
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

app = FastAPI(lifespan=lifespan)


@app.post("/get_netscan")
def get_netscan():
    """
    Trigger a WiFi network scan on the ESP32 and return the results.
    
    Sends a command via MQTT to trigger a network scan and outputs the last 
    network scan data in JSON format.
    Remember that the `previous_scan_result` is optional.
    
    """
    global scan_result, previous_scan_result #Global variables set for you!
    print("get_netscan runs")
    print(MQTT_SCAN_TOPIC)
    mqtt_client.publish(MQTT_COMMAND_TOPIC)
   
    if scan_result:
       return scan_result
    else:
        return JSONResponse(
            status_code=204,
            content=None
        )

@app.get("/get_netscan")
def get_prev_netscan():
    """
    prev netscan version
    
    """
    global scan_result, previous_scan_result #Global variables set for you!
    print("get_prev_netscan runs")
    #print(MQTT_SCAN_TOPIC)
    #mqtt_client.publish(MQTT_COMMAND_TOPIC)
   
    if previous_scan_result:
       return previous_scan_result
    else:
        return JSONResponse(
            status_code=204,
            content=None
        )    



@app.get("/netmap_graph")
def netmap_graph():
    """
    Get a graphical visualization of WiFi networks with fresh scan data.
    
    Triggers a new WiFi scan on the ESP32 and returns a PNG image showing 
    networks and their signal strengths (RSSI). Again, like for the `get_netscan`
    endpoint, the `previous_scan_result` is optional and can be used as a way to
    inform the API user that the scan result is not fresh.

    Don't forget that the scan result is not a JSON object yet! use json.loads() 
    to convert it to a JSON object prior to generating the plot.
    """
    global scan_result, previous_scan_result
    print("netmap_graph runs runs")
    # TODO: Trigger scan, parse JSON, and return PNG visualization
    # Once you implement the logic for sending the MQTT message, you 
    # can copy and paste the code from the CHALLENGE_1_README.md file.

    if scan_result:
        fresh_scan = previous_scan_result != scan_result
        previous_scan_result = scan_result
        try:
            fig = generate_netmap_plot(json.loads(scan_result))
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to generate network map plot: {str(e)}"}
            )
        return StreamingResponse(
            status_code=200,
            content=buf, 
            media_type="image/png",
            headers={"New-Message": f"{fresh_scan}"}
        )
    else:
        return JSONResponse(
            status_code=504,
            content={"error": "Waiting for ESP32 response", "message": "ESP32 has not responded yet! Please wait a moment and try again."}
        )

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "Webserver is running!",
        "service": "WiFi Network Scanner",
        "mqtt_broker": MQTT_BROKER,
        "mqtt_topic": MQTT_TOPIC
    }

if __name__ == "__main__":
    uvicorn.run("wifiscrape_webserver:app", host="127.0.0.1", port=8000, reload=True)