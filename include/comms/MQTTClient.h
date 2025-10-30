#ifndef MQTT_CLIENT
#define MQTT_CLIENT
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include "Wifi-c.h"

// MQTT broker details private
extern const char* mqtt_broker;
extern const int mqtt_port;
extern const char* mqtt_username;
extern const char* mqtt_password;
// MQTT topic for sensor
extern const char* topic_publish_ir;
// The PubSubClient
extern PubSubClient mqttClient;
// Variables for timing
extern long previous_time;
void reconnect();
void setupMQTT();


#endif // MQTT_CLIENT