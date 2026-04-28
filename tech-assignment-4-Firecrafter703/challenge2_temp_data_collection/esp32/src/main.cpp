#include <Arduino.h>
#include <WiFi.h>
#include "ECE140_WIFI.h"
#include "ECE140_MQTT.h"
#include <Wire.h>
#include <Adafruit_AMG88xx.h>

// WiFi credentials
const char* ucsdUsername = UCSD_USERNAME;
String ucsdPassword = String(UCSD_PASSWORD);
const char* wifiSsid = WIFI_SSID;
const char* nonEnterpriseWifiPassword = NON_ENTERPRISE_WIFI_PASSWORD;
unsigned long lastPublish = 0;

// MQTT config
const char* CLIENT_ID = MQTT_CLIENT_ID;
const char* TOPIC_PREFIX = MQTT_TOPIC;


Adafruit_AMG88xx amg;
float pixels[AMG88xx_PIXEL_ARRAY_SIZE];



ECE140_MQTT mqtt(CLIENT_ID, TOPIC_PREFIX);
ECE140_WIFI wifi;




// TODO: Implement MQTT callback function to handle incoming commands
void mqttCallback(char* topic, uint8_t* payload, unsigned int length) {
    String msg = "";
    for (unsigned int i = 0; i < length; i++) {
        msg += (char)payload[i];
    }
    
    Serial.print("[MQTT] Received: ");
    Serial.println(msg);
  
    String message = "{\"device_id\": \"";
    
        
        //float ambtemp = amg.readThermistor();
        message += ESP.getEfuseMac();
        message += "\", \"pixels\": [";
    

    //read pixels
        amg.readPixels(pixels, 64);
    
    //puts the individual pixels in a the message
        for(int i = 0; i < AMG88xx_PIXEL_ARRAY_SIZE-1; i++)
            {
                Serial.print(i);
                message += pixels[i];
                message += ", ";

            }
    //the last pixel, separate from the for loop
        message += pixels[AMG88xx_PIXEL_ARRAY_SIZE-1];
        message += "]}";
        Serial.print("message published");
        mqtt.publishMessage("thermal_data", message);
  //  }

    
}

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.println("Attempting setup WiFi");
    if(strcmp(wifiSsid, "UCSD-PROTECTED") == 0){
        Serial.println("Connecting to UCSD-PROTECTED...");
        wifi.connectToWPAEnterprise(wifiSsid, ucsdUsername, ucsdPassword);
    } else {
        Serial.println("Connecting to Non-Enterprise WiFi...");
        wifi.connectToWiFi(wifiSsid,nonEnterpriseWifiPassword);
    }
    delay(1000);
    


    // TODO: Connect to MQTT broker
    mqtt.connectToBroker();
    // TODO: Subscribe to your topic
    mqtt.subscribeTopic("command");
    // TODO: Set up the callback function.
    mqtt.setCallback(mqttCallback);
    // Initializing the AMG8833 sensor
    Wire.begin();
    if (!amg.begin()) {
        while (1) {
            Serial.println("{\"error\":\"AMG8833 not detected\"}");
            delay(1000);
        }
    }

    delay(100);  // Let sensor boot up
    Serial.println("[Setup] AMG8833 and MQTT ready!");
}


void loop() {
    mqtt.loop(); 
}
