#include <Arduino.h>
#include <WiFi.h>
#include <Adafruit_NeoPixel.h>
#include "ECE140_WIFI.h"
#include "ECE140_MQTT.h"
#include <nlohmann/json.hpp>
#include <iostream>
#include <ctime>

using json = nlohmann::json;

constexpr int NEOPIXEL_PIN = 33;

Adafruit_NeoPixel pixel(1, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
String currentColor = "off";

constexpr const char* CLIENT_ID = "T16"; // fill this, this needs to be unique
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
String color = "";
/** fefe
 * @brief Set colot for the neopixel led
 * 
 * @param r 
 * @param g 
 * @param b 
 */
void setColor(int r, int g, int b) {
    pixel.setPixelColor(0, pixel.Color(r, g, b));
    pixel.show();
}

//This function not only does the callback, but sets the LED lights
void mqttCallback(char* topic, uint8_t* payload, unsigned int length) {
    //Serial.print("mqttCallback function is called\n");
    String message = "";
    for(int i = 0; i < length; i++)
    {

        message += (char) payload[i];

    }

    Serial.print("ESP 32 recieved message: " + message);

    if(message == "red")
    {
        //Serial.println("the red led should turn on");
        color = "red";
        pixel.setPixelColor(0, pixel.Color(255, 0, 0));
        pixel.show();
        delay(500);
        pixel.setPixelColor(0, pixel.Color(255, 0, 0));
        pixel.show();

    }
    if(message == "green")
    {
        //Serial.println("the green led should turn on");
        color = "green";
        pixel.setPixelColor(0, pixel.Color(0, 255, 0));
        pixel.show();
        delay(500);
        pixel.setPixelColor(0, pixel.Color(0, 255, 0));
        pixel.show();

    }
    if(message == "blue")
    {
        
        color = "blue";
        pixel.setPixelColor(0, pixel.Color(0, 0, 255));
        pixel.show();
        delay(500);
        pixel.setPixelColor(0, pixel.Color(0, 0, 255));
        pixel.show();

    }
    if(message == "off")
    {
        
        color = "off";
        pixel.setPixelColor(0, pixel.Color(0, 0, 0));
        pixel.show();
        delay(500);
        pixel.setPixelColor(0, pixel.Color(0, 0, 0));
        pixel.show();

    }
}

void setup() {
    Serial.begin(115200);
    delay(2000);

    pinMode(NEOPIXEL_POWER, OUTPUT);
    digitalWrite(NEOPIXEL_POWER, HIGH);
    delay(10);
    pixel.begin();
    pixel.setBrightness(50);

    // Flash white on startup to verify NeoPixel works
    pixel.setPixelColor(0, pixel.Color(255, 255, 255));
    pixel.show();
    delay(500);
    pixel.setPixelColor(0, pixel.Color(0, 0, 0));
    pixel.show();
    Serial.println("NeoPixel initialized");


    // remaining wifi connection and mqtt initialization
    delay(1000);

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

    json j;

    j["color"] = color.c_str();
    j["timestamp"] = "12345";
    j["rssi"] = WiFi.RSSI();

    std::string jsonToString = to_string(j);
    String message = String(jsonToString.c_str());
    Serial.println(message);
    //delay(100);
    mqtt.publishMessage("signal", message);
    delay(3000);
    //Serial.println("loop is running");
}
