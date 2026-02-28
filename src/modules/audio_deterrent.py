import pygame
import threading
import time
import os
import subprocess

from src.core.event_bus import bus

class AudioDeterrent:

    ALERT_INTERVAL = 5.0 # Seconds between warnings
    last_warning_sent = 0
    last_critical_sent = 0
    def __init__(self):
        print(f"[AUDIO] Initialising...")
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.mixer.init()
        # Load your files
        self.base_dir = "/home/mercy_smart_home/firehazard_detector_system/alert_files"
        # Store the string paths for paplay
        self.path_warning = os.path.join(self.base_dir, "Warning_alert.wav")
        self.path_critical = os.path.join(self.base_dir, "Critical_alert.wav")
    
        # State Flags
        self.is_critical_active = False
        self.warning_count = 0
        self.stop_event = threading.Event()
        self.is_silenced_by_operator = False
        self.current_level = 2
        self.alert_count = 0
        self.last_warning_sent = 0
        self.last_critical_sent = 0

        # Subscriptions
#        bus.subscribe("ALERT_UPDATE", self.handle_alerts)
        bus.subscribe("ALARM_STOP", self.stop_all)
        bus.subscribe("ALERT_UPDATE", self.update_status)
        print("[MOD] Audio Deterrent System Loaded")

        threading.Thread(target=self.handle_alerts, daemon=True).start()


    def update_status(self, event, data):
        """Updates the internal level when sensors.py sends new data"""
        print(f"[AUDIO] Updating status....")
        #self.current_level = data.get('alert_level', 0)
        print(f"[AUDIO] Printing Current_level : {self.current_level}")

    def check_if_stopped_by_web(self):
        """Checks if the NEXT operator hit 'Stop'"""
        try:
            r = requests.get("http://127.0.0.1:5000/admin/api/system_status", timeout=0.3)
            # If alarm_active is False, then we ARE silenced
            return not r.json().get("alarm_active", True)
        except:
            return False



    def handle_alerts(self):
        while(True):
            """Triggered when 0-6 seconds (Warning)"""
            now = time.time()
            #print(f"[AUDIO] Handling warning ...")
#            print(f"[AUDIO] Data: {data}")
#            print(f"""[AUDIO] Current_Level = {self.current_level}, is_critical_active : {self.is_critical_active}
#            Pygame status is not: {pygame.mixer.get_busy()}""")

            if (self.current_level == 2) and (now - self.last_critical_sent) > self.ALERT_INTERVAL:
                self.is_critical_active = True
                #pygame.mixer.fadeout(500) # Immediately kills the Warning sound if it's playing
                #time.sleep(0.2)
                print("[AUDIO] CRITICAL override: Playing Critical Alert")
            # Play critical alert in a loop or once
                print("[AUDIO] Playing Critical Pulse")
                self.play_audio_direct(self.path_critical)
                self.last_critical_sent = now
                #self.snd_critical.play() # Loops until ALARM_STOP

            elif (self.current_level == 1) and (now - self.last_warning_sent) > self.ALERT_INTERVAL: # and (self.alert_count > 3):
                print("[AUDIO] Playing Warning Alert")
                #self.snd_warning.play()
                self.alert_count += 1
                self.play_audio_direct(self.path_warning)
                self.last_warning_sent = now
            time.sleep(0.1)

    def stop_all(self, event_type, data):
        """Resets everything when intruder leaves or NEXT stops alarm"""
        pygame.mixer.stop()
        self.is_critical_active = False
        self.warning_count = 0
        print("[AUDIO] All clear. Audio reset.")

    def play_audio_direct(self, file_path):
        """Bypasses Pygame and uses the system paplay command"""
    # 1. Define the command exactly like your working terminal version
        cmd = [
            "paplay",
            "--device=bluez_sink.41_42_A9_8C_B0_1E.a2dp_sink",
            file_path
        ]
    
    # 2. Set the environment for this specific process
        env = os.environ.copy()
        env["XDG_RUNTIME_DIR"] = "/run/user/1001"
    
        try:
        # Popen starts it in the background so your program doesn't freeze
            subprocess.Popen(cmd, env=env)
            print(f"[AUDIO] Success: Playing {os.path.basename(file_path)} via paplay")
        except Exception as e:
            print(f"[AUDIO] Error: Failed to play via paplay: {e}")




if __name__ == "__main__":
    from src.core.event_bus import bus
    import time
    import threading
    import subprocess

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
    threading.Thread(target=audio_system.handle_alerts, daemon=True).start()
    
    while demo_active:
        #audio_system.play_audio_direct("./alert_files/Warning_alert.wav")
        now = time.time()
        #time.sleep(5.0)
        time_elapsed = now - intruder_start_time

        if (now - intruder_start_time) >= demo_time:
       # 3. Simulate "All Clear" or Remote Stop
            #print("[TEST] T+11s: Sending ALARM_STOP signal.")
            #bus.publish("ALARM_STOP", {})
            time.sleep(0.5)
            demo_active = False
            continue

        if time_elapsed >= CRITICAL_THRESHOLD and (now - last_critical_sent > ALERT_INTERVAL):
        # 2. Simulate 6-Second Threshold Reached -> Critical State
           # print("[TEST] THRESHOLD REACHED! Escalating to CRITICAL...")
            #bus.publish("ALERT_UPDATE", {"option": True})
            last_critical_sent = now


        elif (now - last_warning_sent) > ALERT_INTERVAL:
        # 1. Simulate Motion Detected -> Suspicious State
            #print("[TEST] T+0s: Intruder spotted. Sending WARNING...")
            #bus.publish("ALERT_UPDATE", {"option": True})
            last_warning_sent = now


        #else:
        # 1. Simulate Motion Detected -> Suspicious State
            #print("[TEST] Sending WARNING...")

    print("[TEST] --- Test Complete ---")
