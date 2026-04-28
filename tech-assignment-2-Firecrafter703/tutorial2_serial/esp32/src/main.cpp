#include <Arduino.h>

#define BOOT_BUTTON 0

void setup() {
    Serial.begin(115200);
    pinMode(BOOT_BUTTON, INPUT_PULLUP);
    delay(1000);
}

void loop() {
    int buttonState = digitalRead(BOOT_BUTTON);

    Serial.print("{\"button\":\"");
    Serial.print(buttonState == LOW ? "pressed" : "released");
    Serial.println("\"}");

    delay(1000);
}
