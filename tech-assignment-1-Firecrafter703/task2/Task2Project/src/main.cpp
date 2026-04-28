#include <Arduino.h>


constexpr int LED_PIN = 5;
const int threshold = 13000;

void setup() {

 
  Serial.begin(115200);
  pinMode(LED_PIN, INPUT);
}
//
void loop() {
 
  int value = touchRead(LED_PIN);
  //if contact is sensed by the pin.
  if(value > threshold){
  Serial.print("Pin is sensing contact: ");
  //1 for the print statement is better for values.
  Serial.println(value, 1);
  delay(200);
  }
  //print statements when no contact is being sensed. Will
  //be around 12000.
  else
  {
  Serial.print("Pin is sensing NO contact: ");
  Serial.println(value, 1);
  delay(200);
  }
}

