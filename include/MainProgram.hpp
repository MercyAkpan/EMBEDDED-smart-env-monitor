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
void TakeAirQualityReadingsTask(void *pv);
void mqttTask(void *pv);
void LogAirQualityValues(float ppm, float correctedPPM, float RS, float RS_R0, float analogValue, float voltage, float actualVoltage);
#endif // MAIN_PROGRAM_H