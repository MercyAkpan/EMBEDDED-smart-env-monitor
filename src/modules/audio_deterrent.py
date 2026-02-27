import pygame
import threading
import time
import os
from src.core.event_bus import bus

class AudioDeterrent:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.mixer.init()
        # Load your files
        Base_dir = "/home/mercy_smart_home/firehazard_detector_system/alert_files"
        self.snd_warning = pygame.mixer.Sound(os.path.join(Base_dir,"Warning_alert.wav"))
        self.snd_critical = pygame.mixer.Sound(os.path.join(Base_dir,"Critical_alert.wav"))
        
        # State Flags
        self.is_critical_active = False
        self.warning_count = 0
        self.stop_event = threading.Event()
        self.is_silenced_by_operator = False

        # Subscriptions
        bus.subscribe("WARNING", self.handle_warning)
        bus.subscribe("CRITICAL", self.handle_critical) # This is your 6s+ trigger
        bus.subscribe("ALARM_STOP", self.stop_all)
        print("[MOD] Audio Deterrent System Loaded")


    def check_if_stopped_by_web(self):
        """Checks if the NEXT operator hit 'Stop'"""
        try:
            r = requests.get("http://127.0.0.1:5000/admin/api/system_status", timeout=0.3)
            # If alarm_active is False, then we ARE silenced
            return not r.json().get("alarm_active", True)
        except:
            return False



    def handle_warning(self, event_type, data):
        #print(f"DEBUG: I received {len(args)} arguments.")
        #for i, arg in enumerate(args):
        #    print(f"Arg {i}: {arg}")
        """Triggered when 0-6 seconds (Warning)"""
        if not self.is_critical_active and not pygame.mixer.get_busy():
            print("[AUDIO] Playing Warning Alert")
            self.snd_warning.play()
            #if channel is None:
             #   print(f"[AUDIO] Channel is None")
            #else:
             #   print(f"[AUDIO] SUCCESS: Playing on channel {channel}")
                # Optional: Check volume level of the channel
              #  print(f"[AUDIO] Channel Volume: {channel.get_volume()}")
            #threading.Thread(target=self.snd_warning.play, daemon=True).start()


    def handle_critical(self, event_type, data):
        """Triggered when > 6 seconds or User+Intruder (Critical)"""
        if self.check_if_stopped_by_web():
            print("[AUDIO] Critical event received but IGNORED (Operator Stopped Alarms)")
            return

        if not self.is_critical_active:
            self.is_critical_active = True
            pygame.mixer.fadeout(500) # Immediately kills the Warning sound if it's playing
            time.sleep(0.2)
            print("[AUDIO] CRITICAL override: Playing Critical Alert")
            # Play critical alert in a loop or once
        print("[AUDIO] Playing Critical Pulse")
        self.snd_critical.play() # Loops until ALARM_STOP

    def stop_all(self, event_type, data):
        """Resets everything when intruder leaves or NEXT stops alarm"""
        pygame.mixer.stop()
        self.is_critical_active = False
        self.warning_count = 0
        print("[AUDIO] All clear. Audio reset.")



if __name__ == "__main__":
    from src.core.event_bus import bus
    import time

    # Initialize your class (this starts the bus subscriptions)
    audio_system = AudioDeterrent()

    print("[TEST] --- Starting 10-Second Escalation Test ---")
    demo_active = True
    intruder_start_time = time.time()
    ALERT_INTERVAL = 5.0 # Seconds between warnings
    last_warning_sent = 0
    CRITICAL_THRESHOLD = 10.0
    demo_time = 20.0
    last_critical_sent = 0

    while demo_active:
        now = time.time()
        time_elapsed = now - intruder_start_time

        if (now - intruder_start_time) >= demo_time:
       # 3. Simulate "All Clear" or Remote Stop
            print("[TEST] T+11s: Sending ALARM_STOP signal.")
            bus.publish("ALARM_STOP", {})
            time.sleep(0.5)
            demo_active = False
            continue

        if time_elapsed >= CRITICAL_THRESHOLD and (now - last_critical_sent > ALERT_INTERVAL):
        # 2. Simulate 6-Second Threshold Reached -> Critical State
            print("[TEST] THRESHOLD REACHED! Escalating to CRITICAL...")
            bus.publish("CRITICAL", {"option": True})
            last_critical_sent = now


        elif (now - last_warning_sent) > ALERT_INTERVAL:
        # 1. Simulate Motion Detected -> Suspicious State
            print("[TEST] T+0s: Intruder spotted. Sending WARNING...")
            bus.publish("WARNING", {"option": True})
            last_warning_sent = now


    print("[TEST] --- Test Complete ---")
