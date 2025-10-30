#include "MQTTClient.h"
// ------Global varibales definition
const char* mqtt_broker = "xxx";
const int mqtt_port = 8883;
const char* mqtt_username = "xxx";
const char* mqtt_password = "xxx";
// WiFiClientSecure client;
PubSubClient mqttClient(client);
// MQTT topic for sensor
const char* topic_publish_ir = "esp32/dht11";// Create instances
void setupMQTT() {
  mqttClient.setServer(mqtt_broker, mqtt_port);
}

void reconnect() {
  Serial.println("Connecting to MQTT Broker...");
  while (!mqttClient.connected()) {
    Serial.println("Reconnecting to MQTT Broker...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (mqttClient.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("Connected to MQTT Broker.");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 3 seconds");
      delay(3000);
    }
  }
}