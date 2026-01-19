import RPi.GPIO as GPIO
import time
import threading
from src.core.event_bus import bus

# Pin Setup (Adjust these to your physical wiring)
LED_PIN = 4
BUZZER_PIN = 17

class HardwareAlerts:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        
        self.current_level = 0
        bus.subscribe("ALERT_UPDATE", self.update_status)
        
        # Start the blink thread immediately
        threading.Thread(target=self.blink_loop, daemon=True).start()

    def update_status(self, event, data):
        """Updates the internal level when sensors.py sends new data"""
        self.current_level = data.get('alert_level', 0)

    def blink_loop(self):
        """The background 'heartbeat' for your hardware"""
        while True:
            if self.current_level == 1:
                # LEVEL 1: Only LED Blinks (Slow)
                GPIO.output(LED_PIN, True)
                time.sleep(1)
                GPIO.output(LED_PIN, False)
                time.sleep(1)
                GPIO.output(BUZZER_PIN, False) # Ensure buzzer is OFF

            elif self.current_level == 2:
                # LEVEL 2: LED and Buzzer Pulse (Fast/Urgent)
                GPIO.output(LED_PIN, True)
                GPIO.output(BUZZER_PIN, True)
                time.sleep(1)
                GPIO.output(LED_PIN, False)
                GPIO.output(BUZZER_PIN, False)
                time.sleep(1)

            else:
                # LEVEL 0: Everything Off
                GPIO.output(LED_PIN, False)
                GPIO.output(BUZZER_PIN, False)
                time.sleep(1) # Sleep longer when safe to save CPU


class GSMNotifier:
    def __init__(self):
        bus.subscribe("ALERT_UPDATE", self.process_escalation)
        self.sms_sent = False # Prevent spamming SMS

    def process_escalation(self, event, data):
        # 1. Start AI Location (Takes ~5 seconds)
        level = data.get('alert_level', 0)

        if level == 2 and not self.sms_sent():
            print("📡 [GSM] Critical Level! Starting Location AI and SMS...")
            location = get_ai_location() 
        
        # 2. Send SMS immediately
            send_sms(f"FIRE ALERT at {location}! Temp: {data['temperature']}C")
            self.sms_sent = True
        # 3. Escalation Timer (30s)
            threading.Timer(30.0, self.robo_call_check).start()
        elif level < 2:
            # Reset the flag if the level drops, so it can trigger again later
            self.sms_sent = False


def robo_call_check(self):
        # Here you would check a shared flag or re-check sensors
        print("📞 [GSM] 30s PASSED: Initiating Robo-Call to Police.")

def emergency_logic(alert_queue):
    # Initialize local event subscribers
    hw = HardwareAlerts()
    gsm = GSMNotifier()
    
    while True:
        data = alert_queue.get() # Waits for Alert Level 1 or 2
        bus.publish("ALERT_UPDATE", data)
