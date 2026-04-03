import RPi.GPIO as GPIO
import time
import threading
from src.core.event_bus import bus
from src.modules.audio_deterrent import AudioDeterrent
from src.core import gpio_config

# Pin Setup (Adjust these to your physical wiring)
LED_PIN_1 = gpio_config.PINS["LED_1"]
BUZZER_PIN = gpio_config.PINS["BUZZER"]
LED_PIN_2 = gpio_config.PINS["LED_2"]
LED_PIN_3 = gpio_config.PINS["LED_3"]

class HardwareAlerts:
    def __init__(self):
        self.led_pin_1 = LED_PIN_1
        self.led_pin_2 = LED_PIN_2
        self.led_pin_3 = LED_PIN_3
        self.buzzer_pin = BUZZER_PIN

        self.current_level = 0
        bus.subscribe("ALERT_UPDATE", self.update_status)
        

        # Flags
        self.running = True

        # Start the blink thread immediately
        threading.Thread(target=self.blink_loop).start()


    def update_status(self, event, data):
        """Updates the internal level when sensors.py sends new data"""
        print(f"[HARD_W] Status update...")
        self.current_level = data.get('alert_level', 0)

    def blink_loop(self):
        """The background 'heartbeat' for your hardware"""
        while True:
            if self.running:
                # LEVEL 1: Only LED Blinks (Slow)
                GPIO.output(self.led_pin_1, True)
                time.sleep(1)
                GPIO.output(self.led_pin_1, False)
                time.sleep(1)
                GPIO.output(BUZZER_PIN, False) # Ensure buzzer is OFF


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
    hil = AudioDeterrent()
    
    while True:
        data = alert_queue.get() # Waits for Alert Level 1 or 2
        bus.publish("ALERT_UPDATE", data)
