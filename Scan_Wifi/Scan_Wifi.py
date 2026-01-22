import subprocess
import re
import os

BASE_DIR = "Scan_Wifi"
NETWORK_FILE = os.path.join(BASE_DIR, "KnownNetworks.txt")

def get_filtered_wifi_scan(min_rssi=-80):

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        print(f"📁 Created directory: {BASE_DIR}")


    ALLOWED_BSSIDS = [
        "1e:4e:16:ed:a0:66", #NIT-HUB-1
        "44:1d:64:f6:72:1d", #ANCHOR_02
        "14:2b:2f:c6:4b:5d"  #ANCHOR_03
    ]
    print(f"[SC] Scanning...")
    cmd = "sudo iw dev wlan0 scan"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    stdout, _ = process.communicate()
    data = stdout.decode('utf-8', errors='ignore')

    # Split data into individual router blocks (BSS sections)
    blocks = data.split('BSS ')
    filtered_results = []

    # Keywords that usually indicate a temporary mobile hotspot
    # hotspot_keywords = ['iphone', 'android', 'galaxy', 'pixel', 'phone', 'hotspot']

    for block in blocks[1:]: # Skip the first empty split
        try:
            # Extract BSSID (the first part of the block before the bracket)
            bssid_match = re.search(r'^([0-9a-fA-F:]{17})', block)

            if not bssid_match:
                continue

            bssid = bssid_match.group(1).strip()
            # Extract SSID and Signal
            
            if bssid not in ALLOWED_BSSIDS:
                continue

            ssid_match = re.search(r'SSID: (.*)', block)
            signal_match = re.search(r'signal: (.*?) dBm', block)
            
            if ssid_match and signal_match:

                ssid = ssid_match.group(1).strip()
                rssi = int(float(signal_match.group(1)))
                
                # 1. RANGE FILTER: Ignore signals weaker than -80 dBm
                if rssi < min_rssi:
                    continue
                
                # 2. HOTSPOT FILTER: Ignore if name contains hotspot keywords
                #if any(word in ssid.lower() for word in hotspot_keywords):
                 #   continue
                
                # 3. HIDDEN SSID FILTER: Ignore routers not broadcasting names
                if not ssid or "\\x00" in ssid:
                    continue

                filtered_results.append((bssid, ssid, rssi))
        except Exception:
            continue
    print(f"[SC] Done Scanning...")
    return filtered_results



if __name__ == "__main__":
    print("Testing Filtered Wi-Fi Scan...")
    # min_rssi=-80 ignores anything far away
    results = get_filtered_wifi_scan(min_rssi=-100)
    
    if not results:
        print("No static/strong routers found. Check your antenna or RSSI threshold.")
    else:
        existing_entries = set()
        try:
            print(f"[SC] Saving...")
            if os.path.exists(NETWORK_FILE):
                with open(NETWORK_FILE, "r") as f:
                    for line in f:
                        if line.strip():
                            existing_entries.add(line.strip())
        except FileNotFoundError:
            print(f"[SC] File not found")
            pass

        new_count = 0
        for bssid, ssid, rssi in results:
            entry = f"BSSID:{bssid}, SSID:{ssid}"
            if entry not in existing_entries:
                existing_entries.add(entry)
                new_count += 1

        with open(NETWORK_FILE, "w") as f:
            print(f"[SC] Writing to file.")
            for item in sorted(existing_entries):
                f.write(item + "\n")
            print(f"[SC] Done writing")

        print(f"Scan complete. Added {new_count} new routers. Total unique: {len(existing_entries)} to {NETWORK_FILE}")
