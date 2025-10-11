// my_functions.h
#ifndef MY_FUNCTIONS_H
#define MY_FUNCTIONS_H

#include <Arduino.h>
// void IRAM_ATTR myGlobalISR(void); // Declaration of a global IRAM_ATTR function
void IRAM_ATTR detectsMovement(void);
void blinkLedOff();
void blinkLedOn();

//----Set GPIOs for LED and PIR Motion Sensor
const int led = 23;
const int PIRSensor = 4;
// -----Timer: Auxiliary variables
#define timeSeconds 100
extern unsigned long now;
extern unsigned long lastTrigger;
extern unsigned long lastBlink;
extern unsigned long blinkNow;
extern boolean motionDetectedFlag;
extern boolean startTimer;

#endif // MY_FUNCTIONS_H
