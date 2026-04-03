import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

PINS = {
    "LED_1": 4,
    "LED_2": 17,
    "LED_3": 27,
    "BUZZER": 22
}

def setup():
    for pin in PINS.values():
        GPIO.setup(pin, GPIO.OUT)

def cleanup():
    for pin in PINS.values():
        GPIO.output(pin, False)
    GPIO.cleanup()
