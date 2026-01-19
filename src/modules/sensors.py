import json
import serial
import time
import ssl
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# Strictly use /dev/serial0 for GPIO UART on Pi 3
# Ensure baud rate matches Serial2.begin(115200) on ESP32
def sensor_logic(sensor_queue, mqtt_queue, alert_queue):
    try:
        ser = serial.Serial('/dev/serial0', 115200, timeout=0.1)
        ser.flush() # Clear any old junk data in the buffer
        print("--- Project Apex: Serial Test Initiated ---")
        print("Looking for ESP32 JSON on /dev/serial0...")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not open serial port: {e}")
        exit()
    
    
    # --- Your Credentials ---

    fire_alert_active = False
    last_sent_level = -1

    ser.reset_input_buffer()

    while True:
        print(f"[SENS] Reading data from esp32...")
        data = read_esp32_serial(ser)

        if data:
            print(f"DEBUG [PI-RCV]: {data}")
            level = calculate_alert_level(data.get('temperature', 0), data.get('C02Concentration', 0), last_sent_level)
            print(f"[SENS] This is level: {level}")
            data['alert_level'] = level # Add this to the JSON
            print(f"[SENS] This is alert_level == {data['alert_level']}")


            # Push to the Cloud Worker
            try:
                print(f"[SENS] Sending to WEB")
                sensor_queue.put_nowait(data)
                print(f"[SENS] Sent to WEB")
            except:
                pass # Queue full, skip to stay real-time


            # Push to the Web Worker
            try:
                print(f"[SENS] Sending to MQTT")
                mqtt_queue.put_nowait(data)
                print(f"[SENS] Sent to MQTT")
            except:
                pass


            if level != last_sent_level:
                alert_queue.put(data)
#                fire_alert_active = True
                print(f"[SYS] Alert Level Changed: {last_sent_level} -> {level}")
#                print("[SYS] Emergency Triggered! Alerting Emergency Process...")
                last_sent_level = level
#            elif data.get('C02Concentration',0) < 600:
#                fire_alert_active = False # "Reset" once the air is clear
        
           # This else is optional, but it helps you see if the Serial is empty
        #else:
         #   print("Waiting for data...")

        time.sleep(0.1) # Prevent CPU pegging




def read_esp32_serial(ser):
    if ser.in_waiting > 0:
        try:
            print("[SENS] Reading from esp32")
            # Read the incoming line
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            # Skip empty lines
            if not line or 'nan' in line:
                return None

            # --- SURGERY: Force find the JSON part ---
            if "{" in line and "}" in line:
                start = line.find("{")
                end = line.rfind("}") + 1
                line = line[start:end] 
            else:
                return None # Ignore the "Raw analog value" debug text


            # Convert JSON string to Python Dictionary
            data = json.loads(line)
            if data.get('temperature') == 0 or data.get('humidity') == 0:
                return None
            print(f"[SENS] Received data from esp32")
            return data

        except (json.JSONDecodeError, UnicodeDecodeError):
            # This often happens if the ground wire is loose or baud rates don't match
            print(f"DEBUG: Messy data received -> {line}")
        except Exception as e:
            print(f"DEBUG: Error processing line: {e}")
    return None


#def calculate_alert_level(temp, gas):
 #   if temp > 35 or gas > 8000 or gas > 6000: return 2 # CRITICAL: Fire!
  #  if temp > 33 or gas > 3000:  return 1 # WARNING: Smoke/Heat
   # return 0 # SAFE


# Track the state globally in sensors_logic
def calculate_alert_level(temp, gas, prev_level):
    # --- LEVEL 2 (CRITICAL) ---
    if temp >= 35 or gas >= 6000:
        return 2
    
    # --- LEVEL 1 (WARNING) ---
    if temp >= 33 or gas >= 3000:
        # If we were already at Level 2, stay at Level 2 until we drop further
        if prev_level == 2 and (temp > 34.5 or gas > 5500):
            return 2
        return 1

    # --- LEVEL 0 (SAFE) with Hysteresis ---
    # We only return to 0 if the values drop significantly below the warning line
    # This prevents the "flicker" at 33 degrees
    if temp < 32.5 and gas < 2500:
        return 0
    
    # If we are in the "middle zone", stay at the previous level
    return prev_level
