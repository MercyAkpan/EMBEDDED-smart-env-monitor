#ifndef MAIN_PROGRAM_H
#define MAIN_PROGRAM_H

#include "Wifi-c.h"
#include "AirQuality-Temp_prototype.hpp"
#include "PIR_prototype.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WebServer.h>
#include "GSM.hpp"
#include "LDR.hpp"
#include "MQTTClient.h"
void PresenceSensorTask(void *pv);
void TakeAtmosphericReadingsTask(void *pv);
void mqttTask(void *pv);
#endif // MAIN_PROGRAM_H