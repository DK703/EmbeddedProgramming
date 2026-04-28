import paho.mqtt.client as mqtt
import requests
import json
import os
import sys
import csv
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
API_BASE_URL = "https://sophos.ece140.site"
STUDENT_ID = os.getenv("STUDENT_ID")
CSV_FILE = "my_collection.csv"

current_frame = None
frame_count = 0
empty_count = 0
present_count = 0

TARGET_EMPTY = 50
TARGET_PRESENT = 50


def validate_frame(pixels, label):
    # TODO: Check that we have exactly 64 pixels
    # TODO: Check all temperatures are in valid range (0-80°C)
    # TODO: Check for sensor errors (all pixels identical = likely error)
    # TODO: Warn about potentially mislabeled frames
    print(type(pixels))
    print(len(pixels))
    for i in range(len(pixels)):
        if(i < 0 or i > 80):
            print("doesnt meet threshold")
    # use len instead of pixels.length
    if(len(pixels) != 64):
        return (False, "We do not have exactly 64 pixels")
    if(len(set(pixels)) == 1):
        return (False, "all data is the same for some reason")
    return (True, None)
   
    
    


def upload_frame_with_retry(pixels, label, max_retries=3):
    global frame_count, empty_count, present_count

    is_valid, error = validate_frame(pixels, label)
    if not is_valid:
        print(f"Validation failed: {error}")
        return False

    frame_data = {"label": label, "pixels": pixels}
    headers = {"Authorization": f"Bearer {STUDENT_ID}", "Content-Type": "application/json"}

    # TODO: Implement retry with exponential backoff
    try:
        response = requests.post(f"{API_BASE_URL}/frames", headers=headers, json=frame_data, timeout=10)
        if response.status_code == 201:
            frame_count += 1
            if label == "empty":
                empty_count += 1
            else:
                present_count += 1
            print("frame data is:")
            #print(frame_data)
            save_to_csv(frame_data)
            print(f"Uploaded #{frame_count} as '{label}' (empty: {empty_count}/{TARGET_EMPTY}, present: {present_count}/{TARGET_PRESENT})")
            return True
        else:
            print(f"Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def save_to_csv(frame_data):
    # TODO: Implement CSV backup
    needheader = False
    print("frame data is ")
    print(frame_data)
    print("type of frame data")
    print(type(frame_data))
    '''with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "thermistor", "max_temp", "min_temp"])
    #writer.writerow(["timestamp", "thermistor"])'''

    '''with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([str(timestamp),str(thermistor_temp),max(data["pixels"]),min(data["pixels"])])
reference
 w = csv.DictWriter(f, my_dict.keys())
    w.writeheader()
    w.writerow(my_dict)

'''
    #with open(CSV_FILE, "r") as file:
        #csvfile = csv.DictReader(file)
        #for row in csvfile:
            #print("row is:")
            #print(row["label"])
            #if(row["label"] == "empty"):
                #empty_count = empty_count + 1
            #if(row["label"] == "present"):
                #present_count = present_count + 1
            #frame_count = empty_count + present_count
            


    with open(CSV_FILE, "r") as file:
        line_count = sum(1 for line in file)
        #csvfile = csv.DictReader(file)
        #for row in csvfile:
            #print("label is:")
            #print(row["label"])



    if line_count == 0:
        print("The CSV needs header")
        needheader=True

    else:

        print("multiple lines")

    if(needheader):
        print("need header runs")
        with open(CSV_FILE, "a", newline="") as f:
            writer =csv.writer(f)
            #writer.writeheader()
            header = ['label'] + [f'p{i}' for i in range(64)]
            writer.writerow(header)
        with open(CSV_FILE, "a", newline="") as f:
            writer =csv.writer(f)
            #writer.writeheader()
            writer.writerow([frame_data['label']] + frame_data['pixels'])
        
    else:
        with open(CSV_FILE, "a", newline="") as f:
            writer =csv.writer(f)
            #writer.writeheader()
            writer.writerow([frame_data['label']] + frame_data['pixels'])
        


    pass


def display_ascii_heatmap(pixels):
    if len(pixels) != 64:
        return

    min_t, max_t = min(pixels), max(pixels)
    range_t = max_t - min_t if max_t != min_t else 1
    chars = " ░▒▓█"

    print("\n" + "=" * 26)
    for row in range(8):
        line = " "
        for col in range(8):
            val = pixels[row * 8 + col]
            normalized = (val - min_t) / range_t
            char_idx = min(int(normalized * len(chars)), len(chars) - 1)
            line += chars[char_idx] * 3
        print(line)
    print(f" Min: {min_t:.1f}°C  Max: {max_t:.1f}°C")
    print("=" * 26)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT: {reason_code}")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    global current_frame
    try:
        data = json.loads(msg.payload.decode())
        if 'pixels' in data and len(data['pixels']) == 64:
            current_frame = data['pixels']
    except:
        pass


def print_progress():
    empty_remaining = max(0, TARGET_EMPTY - empty_count)
    present_remaining = max(0, TARGET_PRESENT - present_count)

    print(f"\n{'='*50}")
    print(f"PROGRESS: {frame_count}/100 total")
    print(f"  Empty:   {empty_count}/{TARGET_EMPTY} {'DONE' if empty_remaining == 0 else f'(need {empty_remaining} more)'}")
    print(f"  Present: {present_count}/{TARGET_PRESENT} {'DONE' if present_remaining == 0 else f'(need {present_remaining} more)'}")
    print(f"{'='*50}")


def main():
    global current_frame

    if not STUDENT_ID or STUDENT_ID == "AXXXXXXXX":
        print("ERROR: Set STUDENT_ID in .env!")
        sys.exit(1)

    if not MQTT_TOPIC:
        print("ERROR: Set MQTT_TOPIC in .env!")
        sys.exit(1)

    print("="*50)
    print("Robust Collection Client")
    print(f"Student: {STUDENT_ID}")
    print(f"Target: {TARGET_EMPTY} empty + {TARGET_PRESENT} present = 100 frames")
    print("="*50)
    global empty_count
    global present_count
    global frame_count
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    with open(CSV_FILE, "r") as file:
        csvfile = csv.DictReader(file)
        for row in csvfile:
            print("row is:")
            print(row["label"])
            if(row["label"] == "empty"):
                empty_count = empty_count + 1
            if(row["label"] == "present"):
                present_count = present_count + 1
            frame_count = empty_count + present_count
    try:
        while True:
            if current_frame is None:
                continue

            pixels = current_frame
            current_frame = None
            display_ascii_heatmap(pixels)

            inp = input("\nLabel (0/1/s/p/q): ").strip().lower()

            if inp == 'q':
                break
            elif inp == 's':
                continue
            elif inp == 'p':
                print_progress()
                continue
            elif inp == '0':
                upload_frame_with_retry(pixels, "empty")
            elif inp == '1':
                upload_frame_with_retry(pixels, "present")

            if empty_count >= TARGET_EMPTY and present_count >= TARGET_PRESENT:
                print("\nGOAL REACHED! 100 balanced frames collected!")

    finally:
        print_progress()
        client.loop_stop()


if __name__ == "__main__":
    main()
