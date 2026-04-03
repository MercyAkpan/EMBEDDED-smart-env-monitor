import time
import joblib
import numpy as np
import threading
from collections import deque
# Import your specific project modules
from Scan_Wifi.Scan_Wifi import get_filtered_wifi_scan
from utils.loader import load_golden_routers
from utils.processor import get_smoothed_features

class LocationManager:
    maxlength = 7
    model_path = 'model2.joblib'

    def __init__(self):
        self.enabled = False
        self.is_scanning = False
        self.prediction_buffer = deque(maxlen=self.maxlength)
        self.current_location = "Unknown"
        self.last_stable_location = "Unknown"
        self.lock = threading.Lock()
        self.model = joblib.load(model)
        self.boot_scan_complete = False

        self.model = joblib.load(self.model_path)
        self.anchors = load_golden_routers()
        print(f"LocationManager: Loaded {len(self.anchors)} Golden Routers.")

    def find_location(self):
        """Wraps your raw scanning and AI prediction logic"""
        try:
            # 1. SCAN
            raw_scan = get_filtered_wifi_scan(min_rssi=-100)
            
            # 2. PROCESS
            features = get_smoothed_features(raw_scan, self.anchors)

            # 3. CONFIDENCE GATE
            if sum(features) == 0:
                return "Out of Range"

            # 4. PREDICT
            feature_vector = np.array([features], dtype=np.float32)
            prediction = self.model.predict(feature_vector)[0]
            return prediction
        except Exception as e:
            print(f"Error in find_location: {e}")
            return "Error"


    def update_location_loop():
        while True:
            if not self.enabled and self.boot_scan_complete
                time.sleep(0.5)
                continue
            with self.lock:
                self.is_scanning = True

            raw_result = self.find_location()

            with self.lock:
                self.current_location = raw_result
                if raw_result not in ["Out of Range", "Error"]:
                    self.prediction_buffer.append(raw_result)

                if (len(self.prediction_buffer) >= (self.maxlength - 2)):
                    self.last_stable_location  = self.calculate_majority
                else:
                    self.last_stable_location = "Scanning..."
                self.is_scanning = False
                self.boot_scan_complete = True
            time.sleep(2)


    def calculate_majority(self):
        if not self.prediction_buffer:
            return "Unknown"
        return max(set(self.prediction_buffer), key=list(self.prediction_buffer).count)

    def get_emergency_location(self):
        with self.lock:
            if self.is_scanning:
                return self.last_stable_location
            return self.current_location
