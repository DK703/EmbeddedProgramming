from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
import os
import paho.mqtt.client as mqtt
import requests
import csv
from dotenv import load_dotenv

load_dotenv()

STUDENT_ID = os.getenv("STUDENT_ID")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_BROKER = "broker.emqx.io"
API_URL = "https://sophos.ece140.site"

clients: list[WebSocket] = []
current_frame = None
frame_count = 0
empty_count = 0
present_count = 0

TARGET_EMPTY = 50
TARGET_PRESENT = 50
DUMMYCSV_FILE = "dummy.csv"

def on_message(client, userdata, msg):
    global current_frame
    #print("on message runs!")
    try:
        data = json.loads(msg.payload.decode())
        #print(data)
        if "pixels" in data and len(data["pixels"]) == 64:
            current_frame = data["pixels"]
    except Exception:
        pass


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = on_message


async def broadcast_frames():
    global current_frame
    while True:
        if current_frame and clients:
            msg = json.dumps({
                "type": "frame",
                "pixels": current_frame,
                "stats": {
                    "total": frame_count,
                    "empty": empty_count,
                    "present": present_count,
                    "target_empty": TARGET_EMPTY,
                    "target_present": TARGET_PRESENT
                }
            })
            for client in clients:
                try:
                    await client.send_text(msg)
                except Exception:
                    pass
            current_frame = None
        await asyncio.sleep(0.1)


@asynccontextmanager
async def lifespan(app):
    mqtt_client.connect(MQTT_BROKER, 1883, 60)
    mqtt_client.subscribe(MQTT_TOPIC)
    mqtt_client.loop_start()
    asyncio.create_task(broadcast_frames())
    yield
    mqtt_client.loop_stop()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)


@app.post("/api/collect")
async def collect_frame(request: Request):
    global frame_count, empty_count, present_count
    
    data = await request.json()
    print(data)
    print(json.dumps(data))
    # TODO: Validate that the frame has "label" and "pixels" with 64 values
    
    
    if data.get("label") is None:
        return {"success": False, "error": "there is no label!"}
    if data.get("pixels") is None:
        return {"success": False, "error": "there is no pixels!"}
    if len(data["pixels"]) != 64:
        return {"success": False, "error": "not enough pixels"}
    
    
    # TODO: Build the payload and POST to API_URL/frames with Bearer token
    # TODO: Update counters (frame_count, empty_count, present_count) on success
    # TODO: Return {"success": True/False} with appropriate status

    fieldnames = ['label', 'pixels']

    with open(DUMMYCSV_FILE, "a", newline="") as f:
            writer =csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)

    header = {"Authorization": f"Bearer {STUDENT_ID}"}

    try: 
        response = requests.post(API_URL+"/frames",headers = header, json = data, timeout = 10)
        print(response.status_code)
        if(response.status_code == 201):
            print("201")
            frame_count += 1
            #will this comparison work
            if(data["label"] == "empty"):
                empty_count += 1
            if(data["label"] == "present"):
                present_count +=1

            return {"success": True}

        else:
            print(response.status_code)
            print("else ran, bug alert")
            return {"success": False, "error": "does not run"}
    except Exception as e:
            print(e)
            return {"success": False, "error": "does not run"}

    




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
