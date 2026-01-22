import csv
import os
import time
from Scan_Wifi.Scan_Wifi import get_filtered_wifi_scan
from utils.loader import load_golden_routers
from utils.processor import get_smoothed_features

def collect_data_loop():
    # 1. SETUP: Create folder
    DATA_FOLDER = "training_zones"
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    anchors = load_golden_routers()
    
    while True:
        # 2. INPUT: Room Name
        room_name = input("\nEnter the Room/Zone name (e.g. Server_Room): ").strip()
        if not room_name:
            print("Room name cannot be empty.")
            continue
            
        file_path = os.path.join(DATA_FOLDER, f"{room_name}.csv")

        # 3. OVERWRITE CHECK
        if os.path.exists(file_path):
            choice = input(f"Data for '{room_name}' already exists. Overwrite? (y/n): ")
            if choice.lower() != 'y':
                print("Skipping this room...")
                # Skip to the 'Add another room' question
            else:
                # Proceed to collect and overwrite
                perform_collection(file_path, anchors)
        else:
            # New room, proceed normally
            perform_collection(file_path, anchors)

        # 4. TERMINATION CHECK: Do you want to continue?
        cont = input("\nDo you want to scan another room? (y/n): ").strip().lower()
        if cont != 'y':
            print("\n--- Training Data Collection Finished ---")
            break

def perform_collection(file_path, anchors):
    """Internal helper to handle the actual 30-scan burst."""
    print(f"Starting 30-scan burst. Keep Pi STILL...")
    
    with open(file_path, "w", newline='') as f:
        writer = csv.writer(f)
        scans_max = 30
        for i in range(1, (scans_max + 1)):
            time.sleep(2)
            try:
                raw_data = get_filtered_wifi_scan(min_rssi=-100)
                features = get_smoothed_features(raw_data, anchors)
                writer.writerow(list(features))
                print(f"  [{i}/{scans_max}] Captured...")
            except Exception as e:
                print(f"  [ERROR] Hardware timeout on scan {i}. Retrying...")
                time.sleep(2) # Extra rest on failure
        print(f"Saved to {file_path}")

if __name__ == "__main__":
    collect_data_loop()
