// Methods declarations
#include "PIR_prototype.h"
//---- Libraries added
// #include <OneWire.h>
// #include <DallasTemperature.h>

//
const int oneWireBus = 15;
// OneWire oneWire(oneWireBus);
// DallasTemperature sensors(&oneWire);
 //
//----Set GPIOs for LED and PIR Motion Sensor
const int led = 23;
const int PIRSensor = 4;
// -----Timer: Auxiliary variables
#define timeSeconds 100
unsigned long now = millis();
unsigned long lastTrigger = 0;
unsigned long lastBlink = 0;
unsigned long blinkNow = millis();
boolean motionDetectedFlag = false;
boolean startTimer = false;
//---Checks if motion was detected, sets LED HIGH and starts a timer
void IRAM_ATTR detectsMovement(void)
{
    Serial.println("PIRpinValue:");
    Serial.println(digitalRead(PIRSensor));
    Serial.println("Motion DETECTED......");
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
void setup()
{
    Serial.begin( 115200 ); // Serial port for debugging purposes
    pinMode( PIRSensor, INPUT_PULLUP); // PIR Motion Sensor mode INPUT_PULLUP
    pinMode( led, OUTPUT );
    digitalWrite( led, LOW );
    // Set PIRSensor pin as interrupt, assign interrupt function and set RISING mode
    // attachInterrupt( digitalPinToInterrupt(PIRSensor), detectsMovement, FALLING); 
    // sensors.begin();
    Serial.println("Setup complete");
}
void loop()
{
      Serial.println(digitalRead(PIRSensor));
      delay(500);
    if ((digitalRead(PIRSensor) == HIGH) && !startTimer)
    {
      motionDetectedFlag = false;
      Serial.println( " MOTION DETECTED " );
      Serial.println("Turning ON the LED");
      startTimer = true;
      lastTrigger = millis();
    }
    if (startTimer && ((millis() - lastBlink) > timeSeconds))
    {
      int pinState = digitalRead(led);
      if (pinState == 0)
      {
         blinkLedOn();
      } 
      else
      {
        blinkLedOff();
      }
    }
    now = millis();
    if( startTimer && (now - lastTrigger > ( timeSeconds*50)))
    {
        Serial.println("===========================");
        Serial.println("In here now");
        Serial.println(" Turning OFF the LED " );
        digitalWrite( led, LOW );
        startTimer = false;
    }
    // Serial.println(((millis() - lastTrigger))/ 1000.0);
  // sensors.requestTemperatures(); 
  // float temperatureC = sensors.getTempCByIndex(0);
  // float temperatureF = sensors.getTempFByIndex(0);
  // Serial.print(temperatureC);
  // Serial.println("ºC");
  // Serial.print(temperatureF);
  // Serial.println("ºF");
  // delay(1000);

}
