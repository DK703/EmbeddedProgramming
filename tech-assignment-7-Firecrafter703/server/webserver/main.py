import os
import io
import json
import time
import uvicorn
import asyncio
import bcrypt
import uuid
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, Request,HTTPException, Form, Cookie
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import requests
import csv
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse, RedirectResponse

import mysql.connector
from typing import List
load_dotenv("../esp32/.env")

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_COMMAND_TOPIC = f"{MQTT_TOPIC}/request" # Remember, we need to subscribe to this topic on the ESP32 side!
MQTT_SCAN_TOPIC = f"{MQTT_TOPIC}/scan" # Remember, we need to publish to this topic on the ESP32 side!


clients: list[WebSocket] = []
current_frame = None
temperature = None
macaddress = None
prediction = None
confidence = None
continuous = False


class CommandRequest(BaseModel):
    command: str

class Reading(BaseModel):
    mac_address: str
    pixels: List[float]
    thermistor: float
    prediction: str
    confidence: float

class UsersRequest(BaseModel):
    username: str
    password: str



#INSERT INTO users VALUES (ECE, 123)
#INSERT INTO sessions VALUES (1, fefeifje)
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected to MQTT broker with result code {reason_code}")
    print(MQTT_SCAN_TOPIC)
    client.subscribe(MQTT_SCAN_TOPIC )
    

def on_message(client, userdata, msg):
    global thermal_data
    global macaddress
    global current_frame
    global temperature
    global prediction
    global confidence
    data = msg.payload.decode()
    print("message run")
    print(f"[Received MQTT message] {data}")
    
    
    try:
        # Parse JSON data
        json_data = json.loads(data)
        
        
        #print(json_data)
        #print(f"[Validation Success] Data validated and stored in `thermal_data` global variable")
        thermal_data = json_data
        current_frame = json_data["pixels"]
        temperature = json_data["thermistor"]
        macaddress = json_data["mac_address"]
        prediction = json_data["prediction"]
        confidence = json_data["confidence"]
        #print(thermal_data)
        #print(current_frame)
        print(macaddress)
    except json.JSONDecodeError as e:
        print(f"[Validation Error] Invalid JSON format: {e}")
    except ValidationError as e:
        print(f"[Validation Error] Data does not match required format:")
        print(e)
#not sure which one is better
mqtt_client = mqtt.Client()
#mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect # <- Don't forget to implement the on_connect function!
mqtt_client.on_message = on_message

async def broadcast_frames():
    global current_frame
    print("current frame is ")
    print(current_frame)
    while True:
        if current_frame and clients:
            msg = json.dumps({
                "type": "frame",
                "pixels": current_frame,
                "stats": {
                    "temperature": temperature,
                    "mac_address": macaddress,
                    "prediction": prediction,
                    "confidence": confidence 

                }
            })
            for client in clients:
                try:
                    await client.send_text(msg)
                except Exception:
                    pass
            current_frame = None
        await asyncio.sleep(0.1)




def get_db():
    conn = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )
    try:
        yield conn
    finally:
        conn.close()

def get_current_user(
    session_token: str | None = Cookie(None),
    conn=Depends(get_db),
):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT users.id, users.username FROM sessions "
        "JOIN users ON sessions.user_id = users.id "  # fixed: users_id -> users.id
        "WHERE sessions.session_token = %s",
        (session_token,),
    )
    user = cursor.fetchone()
    cursor.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user

#need for setup!
@asynccontextmanager
async def lifespan(app: FastAPI):
    if MQTT_BROKER:
        mqtt_client.connect(MQTT_BROKER, MQTT_BROKER_PORT, 60)
        mqtt_client.loop_start()
        print(f"MQTT client started, connecting to {MQTT_BROKER}")
        asyncio.create_task(broadcast_frames())
    else:
        print("Warning: MQTT_BROKER not configured")

    for _ in range(30):
        try:
            conn = mysql.connector.connect(
                host=os.environ["DB_HOST"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"]
            )
            cursor = conn.cursor()
            #open sql connects to init.sql. Where the sql code to create or delete
            with open("init.sql") as f:
                for statement in f.read().split(";"):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
            conn.commit()
            cursor.close()
            conn.close()
            break
        except mysql.connector.Error:
            time.sleep(1)
    yield 
    
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


#set up the webpage
@app.get("/")
async def home(request: Request, session_token: str | None = Cookie(None), conn=Depends(get_db)):
    #mqtt_client.publish(MQTT_COMMAND_TOPIC, "test")
    print(session_token)
    print("test")
    print("")
    if session_token:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT users.id FROM sessions "
            "JOIN users ON sessions.user_id = users.id "
            "WHERE sessions.session_token = %s",
            (session_token,),
        )
        user = cursor.fetchone()
        cursor.close()
        #not sure if templets.tempalteResponse is the proper method here...
        if user:
            return templates.TemplateResponse("index.html", {"request": request})
    #return templates.TemplateResponse("home.html", {"request": request})
    return RedirectResponse(url="/login", status_code=303)
#RedirectResponse(url="api/loginpage", status_code=303) templates.TemplateResponse("index.html", {"request": request})
#rubrics 6

@app.post("/api/command")
async def command(body: CommandRequest, user=Depends(get_current_user)):
    
    print("Command received:", body.command)
    #if not session_token:
        #raise HTTPException(status_code=401, detail = "Not authenticated")
   
    if body.command != "get_one" and body.command != "start_continuous" and body.command != "stop":
        raise HTTPException(status_code=400, detail="improper command")
    if body.command == "get_one":
        print("publish runs")
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "get_one")
    if body.command == "start_continuous":
        print("publish runs")
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "start_continuous")
    if body.command == "stop":
        print("publish runs")
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "stop")
    
    

    return {"status": "ok", "command": body.command}



#start with root to check how data is sent
@app.get("/reset")
def root():
    """Health check endpoint"""
    # i want to have it publish
    #print("publish runs")
    #mqtt_client.publish(MQTT_COMMAND_TOPIC, "test")
    
    return {
        "status": "Webserver is running!",
        "service": "WiFi Network Scanner",
        "mqtt_broker": MQTT_BROKER,
        "mqtt_topic": MQTT_TOPIC
    }

#@app.post("/api/command`")
#def commands():
 #   return "commands"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,user=Depends(get_current_user)):
    #if not session_token:
      #  raise HTTPException(status_code=401, detail = "Not authenticated")
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

#part 7 stuff

#| 7.1 | 2 | `POST /api/readings` returns a non-null numeric `id` |
#| 7.2 | 2 | `GET /api/readings` returns a JSON array with HTTP 200 |
#| 7.3 | 2 | `GET /api/readings` includes rows previously POSTed |
#| 7.4 | 2 | `GET /api/readings?device_mac=AA:BB:CC:DD:EE:FF` returns only rows for that MAC |
#| 7.5 | 2 | `DELETE /api/readings/{id}` returns 200 and removes the row |

#docker compose down -v
#docker compose up --

#inserts into both devices and data table. Note that its best if devices go first

@app.post("/api/readings", status_code=200)
def getId(reading: Reading, conn= Depends(get_db), user=Depends(get_current_user)):
    
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
    "INSERT IGNORE INTO devices (mac_address) VALUES (%s)",
    (reading.mac_address,)
    )
    cursor.execute(
        "INSERT INTO data (mac_address, pixels, thermistor_temp, prediction, confidence) VALUES (%s, %s, %s, %s, %s)",
        (reading.mac_address, str(reading.pixels), reading.thermistor, reading.prediction, reading.confidence)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    if not new_id:
        raise HTTPException(status_code=500, detail="insert could not work for some reason")
    return {"id": new_id}


@app.get("/api/readings")

#apparently for get endpoints it doesnt need to have a basemodel or model.
# I dont fully understand why so Ill ask later
def getJSONarray(device_mac: str = None, conn= Depends(get_db), user=Depends(get_current_user)):
    
    #if not session_token:
        #raise HTTPException(status_code=401, detail = "Not authenticated")
    
    cursor = conn.cursor(dictionary=True)
    
    if device_mac:
        cursor.execute("SELECT * FROM data WHERE mac_address = %s", (device_mac,))
    else:
        cursor.execute("SELECT * FROM data")
    allrows = cursor.fetchall()
    cursor.close()
    print(allrows)
    return allrows



@app.delete("/api/readings/{id}")
def deleteReading(id: int, conn=Depends(get_db),user=Depends(get_current_user)):
    #if not session_token:
        #raise HTTPException(status_code=401, detail = "Not authenticated")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM data WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Reading not found")
    return {"detail": "reading deleted"}
   

#part 8
@app.get("/api/devices")
def getDevices(conn= Depends(get_db),user=Depends(get_current_user)):
        #if not session_token:
            #raise HTTPException(status_code=401, detail = "Not authenticated")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT mac_address FROM devices")
        allrows = cursor.fetchall()
        cursor.close()
        print(allrows)
        return allrows


#new endpoints 
@app.get("/me")
def me(user=Depends(get_current_user)):
    return user

'''POST
/api/register
{"username": "...", "password": "..."}
Register a new user. Returns 200 or 201 on success.
'''

@app.post("/api/register")
def registeruser(username: str = Form(...), password: str = Form(...), conn=Depends(get_db), httponly=True):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor = conn.cursor()
#user: Users, sessions: Sessions
    #Users.username = username
    #Users.password_hash = hashed



    #old insert: username, hashed.decode()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed.decode()),
        )
        conn.commit()
    except mysql.connector.IntegrityError:
        cursor.close()
        raise HTTPException(status_code=409, detail="Username already exists")
    user_id = cursor.lastrowid
    session_token = str(uuid.uuid4())
    #Sessions.user_id = user_id
    #Sessions.session_token = session_token
    #old insert: user_id, session_token
    cursor.execute(
        "INSERT INTO sessions (user_id, session_token) VALUES (%s, %s)",
        (user_id, session_token),
    )
    conn.commit()
    cursor.close()
    response = RedirectResponse(url="/", status_code=303)
    ##, secure=True
    response.set_cookie(key="session_token", value=session_token, httponly=True)
    return response


#, current_user=Depends(get_current_user)
@app.get("/login", response_class=HTMLResponse)
def loginpage(request: Request, conn=Depends(get_db)):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def regpage(request: Request, conn=Depends(get_db)):
    return templates.TemplateResponse("register.html", {"request": request})


'''
POST
/api/login
{"username": "...", "password": "..."}
Log in. Returns 200 and sets session_token httpOnly cookie.

'''
@app.post("/api/login")
async def login(request: Request, username: str = Form(None), password: str = Form(None), conn=Depends(get_db), httponly=True):
        
        
        
        if username is None or password is None:
            try:
                body = await request.json()
                username = body.get("username")
                password = body.get("password")
            except:
                pass
    
        if not username or not password:
            raise HTTPException(status_code=401, detail="Missing credentials")


        cursor = conn.cursor(dictionary = True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            print(row)
        #bcrypt.checkpw
            #hashpassword = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            #row["password_hash"], hashpassword
            verify = bcrypt.checkpw(password.encode(), row["password_hash"].encode())
            #if we verify, we add user_id and session token to session table
            if verify:
                #recheck to see if the proper id's are used.. rather confusing
                session_token = str(uuid.uuid4())
                user_id = row["id"]
                cursor.execute(
            "INSERT INTO sessions (user_id, session_token) VALUES (%s, %s)",
            (user_id, session_token),
            )
                conn.commit()
                cursor.close()
                #set response if succesfull
                response = RedirectResponse(url="/posts", status_code=200)
                #, secure=True
                response.set_cookie(key="session_token", value=session_token, httponly=True)
                return response
        #if we went through all the same usernames and unable to find the password
        print("unalb")
        conn.commit()
        cursor.close()
        #proper way to write the failure?
        raise HTTPException(status_code=401, detail="Invalid username or password")
'''
POST
/api/logout
—
Invalidate session and clear cookie. Returns 200.

'''
@app.post("/api/logout")
def logout(session_token: str | None = Cookie(None), conn=Depends(get_db)):
    if session_token:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_token = %s", (session_token,))
        conn.commit()
        cursor.close()
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response
#if __name__ == "__main__":
    #uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)