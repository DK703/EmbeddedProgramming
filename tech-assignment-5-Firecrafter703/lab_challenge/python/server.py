from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import json
import os
import paho.mqtt.client as mqtt
import requests
from dotenv import load_dotenv

load_dotenv()
#MQTT_topic has to be topicprefix/mqtt_topic here....

#ask about the two differences later
STUDENT_ID = os.getenv("STUDENT_ID")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_BROKER = "broker.emqx.io"
API_URL = "https://sophos.ece140.site"

clients: list[WebSocket] = []
current_frame = None
frame_count = 0
empty_count = 0
present_count = 0


def on_message(client, userdata, msg):
    global current_frame
    #print("on message runs")
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
                "stats": {"total": frame_count, "empty": empty_count, "present": present_count}
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


@app.post("/api/label")
async def label_frame(request: Request):
    global frame_count, empty_count, present_count


    data = await request.json()

    # TODO: Build the payload with "label" and "pixels"
    #label and pixes come form data, make a requesth tohugh python(on google slidews)
    # TODO: POST to API_URL/frames with Bearer token authorization
    # TODO: Update counters on success
    # TODO: Return {"success": True/False}

    

    #data["pixels"]
    #data["label"]
    '''
    {'Date': 'Sat, 14 Feb 2026 05:20:48 GMT', 'Content-Type': 'application/json', 'Content-Length': '440', 'Connection': 'keep-alive', 'X-RateLimit-Limit': '1000', 'X-RateLimit-Remaining': '1000', 'Report-To': '{"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=uy0YdjPfrFOvZPigkCQfC%2FQShQDNimwzlMo3%2F3h%2B9RwSc7CBsJ6ZBzAKPWN2Z6zzZ91jf%2BM58wdCqYyJUtZL8Ek8me6brRohSHoKendwNjErVQ7Q27cW0GUX1lHywA%3D%3D"}]}', 'Nel': '{"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}', 'Server': 'cloudflare', 'CF-RAY': '9cda1e4e9dafbd64-LAX', 'alt-svc': 'h3=":443"; ma=86400'}
    '''
    #print(data)
    #return {"success": True}
    header = {"Authorization": f"Bearer {STUDENT_ID}"}
    try: 
        response = requests.post(API_URL+"/frames",headers = header, json = data, timeout = 10)
        print(response.headers)
        #print(response.status_code)
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

        



    return {"success": False, "error": "Not implemented"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
