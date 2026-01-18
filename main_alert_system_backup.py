import time
import numpy as np
# Importing from your new structure
from Scan_Wifi.Scan_Wifi import get_filtered_wifi_scan
from utils.loader import load_golden_routers
from utils.processor import get_smoothed_features

def run_system_test():
    print("--- Project Apex: Initializing System Test ---")
    
    # 1. Load your Anchors (The Golden Routers)
    anchors = load_golden_routers()
    if not anchors:
        print("CRITICAL ERROR: No Golden Routers found in KnownNetworks.txt")
        return
    
    print(f"Loaded {len(anchors)} Golden Routers as anchor points.")

    try:
        while True:
            print("\n[STEP 1] Scanning environment...")
            # 2. Get the filtered scan (BSSID, SSID, RSSI)
            raw_scan = get_filtered_wifi_scan(min_rssi=-100)
            
            # 3. Process and Normalize
            # This turns raw dBm into the positive 0.0 - 80.0 scale
            feature_vector = get_smoothed_features(raw_scan, anchors)
            
            # 4. Show Results and Meaning
            print("[STEP 2] Normalized Feature Vector (Input for ML):")
            print(feature_vector)
            
            print("\n[STEP 3] Analysis of Results:")
            for i, val in enumerate(feature_vector):
                router_bssid = anchors[i]
                if val > 0:
                    # Meaning: The Pi hears this specific anchor
                    print(f" -> Anchor {i} ({router_bssid}): Strength Index {val:.1f} (ACTIVE)")
                else:
                    # Meaning: Anchor is missing or too weak
                    print(f" -> Anchor {i} ({router_bssid}): NOT DETECTED")

            # Explanation for the Exhibition Judges
            print("\n[MEANING]: This vector is the 'Fingerprint' of your current room.")
            print("The ML model will compare these numbers to the training data to pick a room.")
            
            print("\nWaiting 5 seconds for next scan... (Ctrl+C to stop)")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nTest stopped by user.")

if __name__ == "__main__":
    run_system_test()
