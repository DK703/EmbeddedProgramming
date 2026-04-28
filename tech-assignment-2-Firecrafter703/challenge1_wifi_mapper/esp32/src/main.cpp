#include <Arduino.h>
#include <WiFi.h>
#include "ECE140_WIFI.h"
#include "ECE140_MQTT.h"
#include <iostream>
#include <nlohmann/json.hpp>
#include <fstream>
#include <map>
#include <unordered_map>
#include <list>
using namespace std;
using json = nlohmann::json;
using std::to_string;
constexpr const char* CLIENT_ID = "T1"; // fill this, this needs to be unique
constexpr const char* TOPIC_PREFIX = "ECE140A"; //fill this, this needs to match topic prefix from the subscriber.py. Make sure it does not end with / 
constexpr int LED_PIN = 13;


ECE140_MQTT mqtt(CLIENT_ID, TOPIC_PREFIX);
ECE140_WIFI wifi;

// WiFi credentials. Copy and Pasted.
const char* ucsdUsername = UCSD_USERNAME;
String ucsdPassword = String(UCSD_PASSWORD);
const char* wifiSsid = WIFI_SSID;
const char* nonEnterpriseWifiPassword = NON_ENTERPRISE_WIFI_PASSWORD;
unsigned long lastPublish = 0;

void setup() {

    Serial.begin(115200);
    delay(2000);
    Serial.println("attempting setup wifi");
    
    if(strlen(nonEnterpriseWifiPassword)<2){
        Serial.println("ucsd");
        delay(1000);
        wifi.connectToWPAEnterprise(wifiSsid, ucsdUsername, ucsdPassword);
        
    } else {
        Serial.println("local");
        delay(1000);
        wifi.connectToWiFi(wifiSsid,nonEnterpriseWifiPassword);
        
    }
        
delay(5000);
mqtt.connectToBroker();


}

void loop() {
    delay(500);
    mqtt.loop();
    //Serial.print("loop");
    

     
    std::map<int, string> wifiMap;
    
  
    std::map<string, int> list;

    // here are some hints for using wifi network scanner
    // you can get count using
    int numNetworks = WiFi.scanNetworks();

    Serial.println(WiFi.SSID(0));
    json j;


    j["device_id"] = "esp32-001";
    j["timestamp"] = "12345";
    //have to use c_str to change from String to std::string
    j["connected_ssid"] = WiFi.SSID(0).c_str();
    j["connected_rssi"] = WiFi.RSSI(0);
    
    

        //key is the rssi to make getting the strongest signal easier
        for (int i = 0; i <= numNetworks; i++) {
        
             if(WiFi.RSSI(i) < 0 & WiFi.RSSI(i) > -80)
             {
             wifiMap.insert({WiFi.RSSI(i), WiFi.SSID(i).c_str()});
             }
    }
    
    int limit = 0;

    
        //auto individual: wifiMap
        //this is how i get a pair for the json list. i will add it to the array each time.
        for(auto individual= wifiMap.rbegin(); individual != wifiMap.rend(); individual++)
        {
            if (limit == 10) {
                break;
                }
      
            std::pair<string, int> networkPair = {individual->second, individual->first};
            list.insert(networkPair);
           

            Serial.println(networkPair.first.c_str());

            limit++;
        }
 
     
 j["network"] = list; 
 
  std::string jsonToString = to_string(j);
  String BigString = String(jsonToString.c_str());
  Serial.println(BigString);
  mqtt.publishMessage("signal", BigString);





    delay(5000);
    
}
