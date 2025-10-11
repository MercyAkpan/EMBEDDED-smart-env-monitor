// Methods declarations
#include "PIR_prototype.h"
//---- Libraries added
// #include <OneWire.h>
// #include <DallasTemperature.h>

//
// const int oneWireBus = 15;
// OneWire oneWire(oneWireBus);
// DallasTemperature sensors(&oneWire);
 //

//---Checks if motion was detected, sets LED HIGH and starts a timer
void IRAM_ATTR detectsMovement(void)
{
    // Serial.println("PIRpinValue:");
    // Serial.println(digitalRead(PIRSensor));
    // Serial.println("Motion DETECTED......");
    motionDetectedFlag = true;
}
// Blink LED
void blinkLedOn()
{
    digitalWrite(led, HIGH);
    // Serial.print("Led is on");
    lastBlink = millis();
}
void blinkLedOff()
{
    digitalWrite(led, LOW);
    lastBlink = millis();
}

