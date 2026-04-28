#include <Arduino.h>

//variable declaraitions go here:

constexpr int LED_PIN = 13;


// put function declarations here:

void setup() {
 
 Serial.begin(115200);
 pinMode(LED_PIN, OUTPUT);
}
//dot helper function
void dot()
{
 digitalWrite(LED_PIN, HIGH); 
 delay(300);           // 300ms pulse
 digitalWrite(LED_PIN, LOW);   
 //delay(300);  
}
//dash helper function
void dash()
{
 digitalWrite(LED_PIN, HIGH); 
 delay(900);           // 900ms pulse
 digitalWrite(LED_PIN, LOW);  
 //delay(900);   
}
//helper function for delay after dash or dot
void dashdotdelay()
{
  delay(300);
}
//Helper function for word delay. Discontinued after D and i.
void worddelay()
{
  delay(900);
}

void loop() {
  // put your main code here, to run repeatedly:
   //D
   dash();
   dashdotdelay();
   dot();
   dashdotdelay();
   dot();
   worddelay();
   Serial.println("D printed");
   //i
   dot();
   dashdotdelay();
   dot();
   worddelay();
   Serial.println("i printed");
   //l
   dot();
   dashdotdelay();
   dash();
   dashdotdelay();
   dot();
   dashdotdelay();
   dot();
   delay(900);
   Serial.println("l printed");
  //l
  
   dot();
   dashdotdelay();
   dash();
   dashdotdelay();
   dot();
   dashdotdelay();
   dot();
   delay(900);
   Serial.println("l printed");
   //o

   dash();
   dashdotdelay();
   dash();
   dashdotdelay();
   dash();
   delay(900);
   Serial.println("o printed");
   //n

   dash();
   dashdotdelay();
   dot();
   dashdotdelay();
   delay(900);
   Serial.println("n printed");


   //delay before reset
   delay(2000);
}