import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import time
import ssl



def mqtt_worker(mqtt_queue):
    # --- CONFIGURATION (Move this here from sensor_logic) ---
    mqtt_broker = "53e98d6c8c614f1493d9b19b996ab3a2.s1.eu.hivemq.cloud"
    mqtt_port = 8883
    topic = "esp32/all_sensor"
    username = "AkpanMercy"
    password = "Memehive2$"

    # --- CONNECTION LOGIC ---
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="Pi3_Gateway", userdata=None, protocol=mqtt.MQTTv5)
    client.username_pw_set(username, password)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to HiveMQ Cloud!")
        else:
            print(f"Failed to connect, return code {rc}")

    client.on_connect = on_connect
    client.connect(mqtt_broker, mqtt_port)
    client.loop_start() # Starts a background thread for the connection


    # --- THE WORKER LOOP ---
    while True:
        #print(f"[MQTT] In the MQTT")
        # This blocks until something is put into mqtt_queue
        #print(f"[MQTT] Getting data for MQTT")
        data = mqtt_queue.get() 
        #print(f"[MQTT] Gotten data for MQTT")
        try:
            # Publish the data received from the sensor process
         #   print(f"[MQTT] Publishing data to MQTT")
            client.publish(topic, json.dumps(data), qos=0)
            print(f"[MQTT] Published data to MQTT")
            # print(f"📡 [CLOUD] Data sent to HiveMQ")
        except Exception as e:
            print(f"📡 [MQTT] Publish Error: {e}")
