import multiprocessing as mp
import time
import json
import RPi.GPIO as GPIO
from src.modules.sensors import sensor_logic
from src.modules.emergency import emergency_logic
from src.modules.web_server import run_web_process
from src.modules.mqtt import mqtt_worker 
from src.modules.audio_deterrent import AudioDeterrent
from src.core import gpio_config

gpio_config.setup()
if __name__ == "__main__":
    print("[INIT] Project Apex: Fire Hazard System Starting...")

    # 1. Communication Queues
    # sensor_queue: Sensors -> Web Server (for Chart.js)
    # alert_queue: Sensors -> Emergency (to trigger GSM/Location)
    sensor_queue = mp.Queue()
    alert_queue = mp.Queue()
    mqtt_queue = mp.Queue(maxsize=10)

    # 2. Start Independent Processes
    # Process 1: Constant Serial Read & MQTT Publish
    p_sensors = mp.Process(target=sensor_logic, args=(sensor_queue, mqtt_queue, alert_queue))
    p_mqtt = mp.Process(target=mqtt_worker, args=(mqtt_queue, ))
    # Process 2: Flask Web Server (Chart.js + Camera)
    p_web = mp.Process(target=run_web_process, args=(sensor_queue,))

    # Process 3: Emergency Responder (Positioning + GSM)
    p_emergency = mp.Process(target=emergency_logic, args=(alert_queue,))

    p_mqtt.start()
    p_web.start()
    p_emergency.start()

    p_sensors.start()
    try:
        while True:
            time.sleep(1)
    finally: #KeyboardInterrupt
        print("[STOP] Shutting down Project Apex...")
        p_sensors.terminate()
        p_sensors.join(timeout=2)
        p_web.terminate()
        p_web.join(timeout=2)
        p_emergency.terminate()
        p_emergency.join(timeout=2)
        p_mqtt.terminate()
        p_mqtt.join(timeout=2)

        gpio_config.cleanup()  # Ensure LEDs are turned off
        print("[STOP] Project Apex shutdown complete.")

