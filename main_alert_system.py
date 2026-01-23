import time
import joblib
import numpy as np
# Importing from your project structure
from collections import deque
from Scan_Wifi.Scan_Wifi import get_filtered_wifi_scan
from utils.loader import load_golden_routers
from utils.processor import get_smoothed_features

prediction_buffer = deque(maxlen=7)
def run_project_apex():
    print("--- Project Apex: Initializing Alert System ---")

    # 1. SETUP: Load the AI Brain and Golden Routers
    try:
        MODEL_NAME = 'model2.joblib'
        model = joblib.load(MODEL_NAME)
        anchors = load_golden_routers()
        if not anchors:
            print("CRITICAL ERROR: No Golden Routers found in KnownNetworks.txt")
            return
        print(f"Loaded {len(anchors)} Golden Routers. AI Model ready.")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load {MODEL_NAME}: {e}")
        print("Hint: Did you run Train_Model.py first?")
        return

    try:
        while True:
            print("\n[STEP 1] Scanning environment...")
            # 2. SCAN: Capture raw Wi-Fi data
            raw_scan = get_filtered_wifi_scan(min_rssi=-100)

            # 3. PROCESS: Normalize using your 100 + RSSI math
            features = get_smoothed_features(raw_scan, anchors)
            
            # --- NEW: CONFIDENCE GATE (The ESP32 Counterpart Check) ---
            # If the sum is 0, we don't hear ANY of our fixed beacons
            if sum(features) == 0:
                print("[STATUS] Searching for Golden Anchors... (OUT OF RANGE)")
                time.sleep(2)
                continue 

            # 4. PREDICT: Convert to float32 matrix and ask the AI
            feature_vector = np.array([features], dtype=np.float32)
            prediction = model.predict(feature_vector)[0]

            prediction_buffer.append(prediction)
            smoothed_prediction = max(set(prediction_buffer), key=list(prediction_buffer).count)

            # 5. OUTPUT: Show the location to the user/judges
            print(f"[BUFFER] History: {list(prediction_buffer)}")
            print(f"[STEP 2] AI DECISION: You are currently at -> **{smoothed_prediction}**")

            # --- 6. FIRE ALERT LOGIC (Placeholder for next phase) ---
            # smoke = read_smoke_sensor() 
            # if smoke > threshold:
            #     print(f"!!! ALERT: Fire detected at {prediction} !!!")
            #     send_gsm_alert(prediction)

            print("\nWaiting 2 seconds for next update...")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nSystem shut down by user.")

if __name__ == "__main__":
    run_project_apex()
