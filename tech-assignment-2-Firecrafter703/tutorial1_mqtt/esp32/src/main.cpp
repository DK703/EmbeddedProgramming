#include <Arduino.h>
#include <WiFi.h>
#include "ECE140_WIFI.h"
#include "ECE140_MQTT.h"



constexpr const char* CLIENT_ID = "T167"; // fill this, this needs to be unique
constexpr const char* TOPIC_PREFIX = "ECE140A"; //fill this, this needs to match topic prefix from the subscriber.py. Make sure it does not end with / 
constexpr int LED_PIN = 13;


ECE140_MQTT mqtt(CLIENT_ID, TOPIC_PREFIX);
ECE140_WIFI wifi;

// WiFi credentials
const char* ucsdUsername = UCSD_USERNAME;
String ucsdPassword = String(UCSD_PASSWORD);
const char* wifiSsid = WIFI_SSID;
const char* nonEnterpriseWifiPassword = NON_ENTERPRISE_WIFI_PASSWORD;
unsigned long lastPublish = 0;


//makes the ESP32 itself a subscriber
//nothing to do with looping
void mqttCallback(char* topic, uint8_t* payload, unsigned int length)
{

    Serial.print("mqttCallback function is called\n");

    String message = "";
    for(int i = 0; i < length; i++)
    {

        message += (char) payload[i];

    }

    Serial.print("ESP 32 recieved message: " + message);
    digitalWrite(LED_PIN, HIGH); 

}

void setup() {
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    delay(2000);
    Serial.println("attempting setup wifi");
    if(strlen(nonEnterpriseWifiPassword)<2){
        wifi.connectToWPAEnterprise(wifiSsid, ucsdUsername, ucsdPassword);
        Serial.println("ucsd");
    } else {
        wifi.connectToWiFi(wifiSsid,nonEnterpriseWifiPassword);
        Serial.println("local");
    }
    delay(1000);
    mqtt.connectToBroker();
    //its mqtt that calls it, not the setup!!!!
    mqtt.setCallback(mqttCallback);
    mqtt.subscribeTopic("command");

}

void loop() {
    mqtt.loop();
  
    String wifiName = WiFi.SSID();
    int rssi = WiFi.RSSI();
    //char msg[100];
    String msg = "{\"device\":\"esp32-001\", \"wifiName:\"";
    msg += wifiName;
    msg += ",\"RRSI\":";
    msg += String(WiFi.RSSI());
    msg += "}";

   // sprintf(msg, "{\"device\":\"esp32-001\",\"rssi\":%d \"WifiName\":%s}", rssi, wifiName);
    //sprintf(msg, "{\"device\":\"esp32-001\",\"rssi\":%d \"WifiName\":%s}", rssi, wifiName);
    mqtt.publishMessage("signal", String(msg));
    Serial.print("main.cpp print message");
    //Serial.print("Printing message \n");
    //Serial.println(msg);

    delay(5000);
}
 
