#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <Adafruit_AMG88xx.h>
#include "ECE140_WIFI.h"
#include "ECE140_MQTT.h"

// Challenge 2 - Request-Response with Auto Mode Support
// Commands: "request" (one-time), "auto" (start streaming), "stop" (stop streaming)

constexpr const char* CLIENT_ID = "T64";
constexpr const char* TOPIC_PREFIX = "ECE140A";
bool dataRequested = false;

Adafruit_AMG88xx amg;
float pixels[AMG88xx_PIXEL_ARRAY_SIZE];
ECE140_MQTT mqtt(CLIENT_ID, TOPIC_PREFIX);
ECE140_WIFI wifi;

// WiFi credentials
const char* ucsdUsername = UCSD_USERNAME;
String ucsdPassword = String(UCSD_PASSWORD);
const char* wifiSsid = WIFI_SSID;
const char* nonEnterpriseWifiPassword = NON_ENTERPRISE_WIFI_PASSWORD;

/**
 * @brief Callback function for MQTT messages
 */
void mqttCallback(char* topic, uint8_t* payload, unsigned int length) {
    String message = "";
    for (unsigned int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("[MQTT] Received: ");
    Serial.println(message);
    //important because this means that we will only publish a message
    //when we recieve a message!
    dataRequested = true;

    
}


void setup() {
    Serial.begin(115200);
    delay(2000);

    // Connect to WiFi
    if (strlen(nonEnterpriseWifiPassword) < 2) {
        wifi.connectToWPAEnterprise(wifiSsid, ucsdUsername, ucsdPassword);
    } else {
        wifi.connectToWiFi(wifiSsid, nonEnterpriseWifiPassword);
    }

    // Connect to MQTT broker
    mqtt.connectToBroker();
    
    mqtt.setCallback(mqttCallback);  // Must be AFTER connectToBroker (it recreates client)
    // Initialize AMG8833
    Wire.begin();
    if (!amg.begin()) {
        while (1) {
            Serial.println("{\"error\":\"AMG8833 not detected\"}");
            delay(1000);
        }
    }

    delay(100);  // Let sensor boot up
    Serial.println("[Setup] AMG8833 and MQTT ready!");
    delay(100);
    mqtt.subscribeTopic("request"); //not sure if subscribeTopic should go here
    delay(100);
}

void loop() {
    //should the if statement be below the loop?
    mqtt.loop();
   
    String message = "";
    if(dataRequested)
    {
        //read thermal data and publish
        //set the boolean to false
        dataRequested = false;
        String message = "{\"thermistor\": ";
    //read thermisotr
        float ambtemp = amg.readThermistor();
        message += ambtemp;
        message += ", \"pixels\": [";
    

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
        mqtt.publishMessage("response", message);
    }

    
    
}
