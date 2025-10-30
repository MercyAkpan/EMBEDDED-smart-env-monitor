#ifndef AIRQUALITY
#define AIRQUALITY


#include <ArduinoJson.h>
#include "DHT.h"
#include "MQ135.h"
#include "Wifi-c.h"
// #include "AirQuality-Temp_prototype.hpp"
#define MQ135_PIN 34  // Use a true ADC-capable pin on ESP32
#define RLOAD 1.0
#define RZERO 38.0
#define VOLTAGE_DIVIDER_RATIO (5.0 / 2.86)  // 1.748
// DHT11 SETTINGS 
#define DHTPIN 33
#define DHTTYPE DHT11
extern DHT dht;

const int ledPin = 22;
extern bool ledState;

//BUZZER configuration
const int BuzzerPin = 12;

// MQ135 SETTINGS

extern MQ135 gasSensor;

extern unsigned long lastTimeBotRan;
const unsigned long BOT_MTBS = 1000;
extern WebServer server;

void Controller(const int pin, bool value);
void handleLedOff();
void handleLedOn();
void handleReadings();
void handleRoot();
void handleNewMessages(int numNewMessages);


#endif// AIRQUALITY