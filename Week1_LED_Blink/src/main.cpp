#include <Arduino.h>

//variable declaraitions go here:

constexpr int LED_PIN = 13;
constexpr int BUTTON_PIN = 0;


// put function declarations here:

void setup() {
  // put your setup code here, to run once:
 Serial.begin(115200);
 //pinMode(BUTTON_PIN, INPUT_PULLUP);
 pinMode(LED_PIN, OUTPUT);
}

void dot()
{
 digitalWrite(LED_PIN, HIGH); 
 delay(300);           // 300ms pulse
 digitalWrite(LED_PIN, LOW);   
 //delay(300);  
}
void dash()
{
 digitalWrite(LED_PIN, HIGH); 
 delay(900);           // 900ms pulse
 digitalWrite(LED_PIN, LOW);  
 //delay(900);   
}

void dashdotdelay()
{
  delay(300);
}

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
   Serial.println("D");
   //i
   dot();
   dashdotdelay();
   dot();
   worddelay();
   Serial.println("i");
   //l
   dot();
   dashdotdelay();
   dash();
   dashdotdelay();
   dot();
   dashdotdelay();
   dot();
   delay(900);
  //  worddelay();
  // Serial.println("l");
  //l
   dot();
   dashdotdelay();
   dash();
   dashdotdelay();
   dot();
   dashdotdelay();
   dot();
   delay(900);
   //o
   dash();
   dashdotdelay();
   dash();
   dashdotdelay();
   dash();
   delay(900);
   //n

   dash();
   dashdotdelay();
   dot();
   dashdotdelay();
   delay(900);
   

   delay(2000);
}