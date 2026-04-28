#include <Arduino.h>
#include <WiFi.h>
#include "ECE140_WIFI.h"
#include "ECE140_MQTT.h"
#include <ArduinoJson.h>
#include <map>
constexpr const int NUM_NETWORKS = 10;
// WiFi credentials
const char* ucsdUsername = UCSD_USERNAME;
String ucsdPassword = String(UCSD_PASSWORD);
const char* wifiSsid = WIFI_SSID;
const char* nonEnterpriseWifiPassword = NON_ENTERPRISE_WIFI_PASSWORD;
unsigned long lastPublish = 0;

// MQTT config
const char* CLIENT_ID = MQTT_CLIENT_ID;
const char* TOPIC_PREFIX = MQTT_TOPIC;



ECE140_MQTT mqtt(CLIENT_ID, TOPIC_PREFIX);
ECE140_WIFI wifi;

//StaticJsonDocument<200> json;

// TODO: Implement a helper function to scan networks and publish JSON to MQTT

void publish(String message)
{
     String msg = message;
     msg += ", \"networks\":[";

     int numNetworks = WiFi.scanNetworks();
     std::map<int, String> wifiValueMap;
     std::map<String, int> list;
     for (int i = 0; i <= numNetworks; i++) {
        
             if(WiFi.RSSI(i) < 0 & WiFi.RSSI(i) > -80)
             {
             wifiValueMap.insert({WiFi.RSSI(i), WiFi.SSID(i).c_str()});
             }
    }

        int limit = 0;

    
        //auto individual: wifiMap
        //this is how i get a pair for the json list. i will add it to the array each time.
        for(auto individual= wifiValueMap.rbegin(); individual != wifiValueMap.rend(); individual++)
        {
            if (limit == 10) {
                break;
                }
            if (limit > 0)
            {
                msg += ",";
            }
            std::pair<String, int> networkPair = {individual->second, individual->first};
            list.insert(networkPair);
            msg += "{";
            msg += "\"ssid\": \"";
    
            msg += individual->second;
            msg += "\",\"rssi\": ";
            msg += individual->first;
            msg+= "}";
           

            Serial.println(networkPair.first);
            Serial.println(networkPair.second);

            limit++;
        }
 msg += "]}";
 Serial.print(msg);
 mqtt.publishMessage("scan", msg);

}

// TODO: Implement the MQTT callback function to trigger scans
void mqttCallback(char* topic, uint8_t* payload, unsigned int length) {


    
    //base for testing connectivity without wifi scan...
    Serial.println(WiFi.SSID());
    String message= "{\"device_id\":\"esp32-001\",";
    message += "\"connected_ssid\": \"";
    //message += "\"test\"";
    message += WiFi.SSID();
    message += "\",\"connected_rssi\": ";
    message += WiFi.RSSI();
 
    Serial.print(message);
    
    delay(500);
    publish(message);



    //important because this means that we will only publish a message
    //when we recieve a message!

    Serial.println(message);
    //do we need a message and a boolean for this case??
    //dataRequested = true;
    
}

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.println("Attempting setup WiFi");
    if(strcmp(wifiSsid,"UCSD-PROTECTED") == 0){
        Serial.println("Connecting to UCSD-PROTECTED...");
        wifi.connectToWPAEnterprise(wifiSsid, ucsdUsername, ucsdPassword);
    } else {
        Serial.println("Connecting to Non-Enterprise WiFi...");
        wifi.connectToWiFi(wifiSsid,nonEnterpriseWifiPassword);
    }
    delay(1000);
    // TODO: Connect to MQTT broker
    mqtt.connectToBroker();
    // TODO: Set up the callback function
    mqtt.setCallback(mqttCallback);
    // TODO: Subscribe to the "command" topic
    mqtt.subscribeTopic("command"); 
    
    
}

void loop() {
    mqtt.loop(); // We don't need to do anything here, the callback function will handle all of your logic!
}