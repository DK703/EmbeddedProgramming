from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import requests
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

SOPHOS_API_URL = "https://sophos.ece140.site"
STUDENT_ID = os.getenv("STUDENT_ID")

app = FastAPI(title="Dataset Explorer")
#templates = Jinja2Templates(directory="explorer/templates")
templates = Jinja2Templates(directory="templates")
#app.mount("/static", StaticFiles(directory="explorer/static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")
connected_clients: list[WebSocket] = []

#empty,17.25,17.5,17.25,18.0,17.75,17.75,17.5,18.0,17.5,17.0,17.25,17.25,17.75,17.75,17.5,18.0,17.0,17.0,17.75,18.0,17.0,17.5,17.5,17.75,16.75,17.75,17.25,17.5,17.75,17.0,17.5,17.75,17.25,17.5,17.5,17.5,17.75,17.0,17.25,17.25,17.5,17.5,17.0,17.5,17.25,16.75,17.0,17.75,17.25,16.75,16.75,17.5,17.25,17.0,17.25,17.5,17.0,16.75,17.25,16.5,17.0,17.25,17.0,17.5
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/stats")
async def get_stats():
    # TODO: Fetch from Sophos /dataset/stats
    print(STUDENT_ID)
    header = {"Authorization": f"Bearer {STUDENT_ID}"}
    try:
        print("get stats has run with response code:")
        
        response = requests.get(SOPHOS_API_URL + "/dataset/sets", headers=header, timeout=10)
        print(response.status_code)
        
        if(response.status_code == 200):
            return response.json()
        else:
            return {"success": False, "error": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

   


@app.get("/api/sample")
async def get_sample(label: str = None, n: int = 6):
    # TODO: Fetch from Sophos /dataset/sample
    header = {"Authorization": f"Bearer {STUDENT_ID}"}
    try:
        print("get sample ran with response code: ")
        response = requests.get(SOPHOS_API_URL + "/dataset/sample", headers=header, timeout=10)
        print(response.status_code)
        if(response.status_code == 200):
            return response.json()
        else:
            return {"success": False, "error": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

    


@app.post("/api/upload")
async def upload_frame(request: Request):
    # TODO: Forward frame to Sophos POST /frames with Bearer auth
    data = await request.json()

    header = {"Authorization": f"Bearer {STUDENT_ID}"}

    try: 
        #is the sophos_api_url needed?
        print("upload frame has ran")
        response = requests.post(SOPHOS_API_URL+"/frames",headers = header, json = data, timeout = 10)
        print(response.status_code)
        if(response.status_code == 201):
            print("201")
          

            return {"success": True}

        else:
            print(response.status_code)
            print("else ran, bug alert")
            return {"success": False, "error": "does not run"}
    except Exception as e:
            print(e)
            return {"success": False, "error": "does not run"}
    


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    header = {"Authorization": f"Bearer {STUDENT_ID}"}
    try:
        while True:
            
            response = requests.get(SOPHOS_API_URL+"/dataset/stats",headers = header, timeout = 10)
            print("ws/live has run:")
            print(response.status_code)
            if response.status_code == 200:
                await websocket.send_json(response.json())
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        connected_clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
