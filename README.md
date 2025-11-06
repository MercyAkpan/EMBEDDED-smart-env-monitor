# EMBEDDED-smart-env-monitor
An ESP32-based system that monitors air quality, temperature, and presence, with wireless feedback and data logging for smarter home/office environments.
Smart Environmental Monitor

## 🔹 Short Description

A low-power embedded IoT device built with the ESP32 to continuously monitor indoor air quality and environmental conditions in homes and offices. The system integrates multiple sensors (air quality, temperature, humidity, pressure, gas detection) with wireless communication, efficient power management, and real-time feedback.

## 🔹 Project Aims:

- Helps track air quality trends that affect health and productivity.

- Demonstrates integration of hardware, firmware, and cloud communication.

- Designed with scalability in mind (from a single room to multiple locations).

- Useful both for academic demonstration and as a portfolio project for recruiters.

## 🔹 Features (recruiter-friendly bullet points)

📡 Wireless communication (Wi-Fi/MQTT for cloud & dashboard integration)

🌡️ Multi-sensor fusion: Dht11 (temperature, humidity) + Air quality sensors (MQ135)

⚡Use of dual power: 
-  DC power via an AC-DC converter
-  DC power via a DC-DC converter.

💡 Feedback system: onboard LED/buzzer alerts when poor air quality is detected

📊 Data storage: Micro SD card and cloud logging via firebase realtime database

📊 Cloud & dashboard integration including: NodeRED + Firebase + HiveMQCloud

📊 Future extension:
- Use of InfluxDB + Grafana for more powerful data manipulation and visualisation.
