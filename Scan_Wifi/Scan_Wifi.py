import subprocess
import re

def get_filtered_wifi_scan(min_rssi=-80):
    cmd = "sudo iw dev wlan0 scan"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    stdout, _ = process.communicate()
    data = stdout.decode('utf-8', errors='ignore')

    # Split data into individual router blocks (BSS sections)
    blocks = data.split('BSS ')
    filtered_results = []

    # Keywords that usually indicate a temporary mobile hotspot
    hotspot_keywords = ['iphone', 'android', 'galaxy', 'pixel', 'phone', 'hotspot']

    for block in blocks[1:]: # Skip the first empty split
        try:
            # Extract BSSID (the first part of the block before the bracket)
            bssid_match = re.search(r'^([0-9a-fA-F:]{17})', block)
            # Extract SSID and Signal
            ssid_match = re.search(r'SSID: (.*)', block)
            signal_match = re.search(r'signal: (.*?) dBm', block)
            
            if bssid_match and ssid_match and signal_match:
                bssid = bssid_match.group(1).strip()
                ssid = ssid_match.group(1).strip()
                rssi = int(float(signal_match.group(1)))
                
                # 1. RANGE FILTER: Ignore signals weaker than -80 dBm
                if rssi < min_rssi:
                    continue
                
                # 2. HOTSPOT FILTER: Ignore if name contains hotspot keywords
                if any(word in ssid.lower() for word in hotspot_keywords):
                    continue
                
                # 3. HIDDEN SSID FILTER: Ignore routers not broadcasting names
                if not ssid or "\\x00" in ssid:
                    continue

                filtered_results.append((bssid, ssid, rssi))
        except Exception:
            continue

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
            with open("KnownNetworks.txt", "r") as f:
                for line in f:
                    existing_entries.add(line.strip())
        except FileNotFoundError:
            pass

        new_count = 0
        for bssid, ssid, rssi in results:
            entry = f"BSSID:{bssid}, SSID:{ssid}"
            if entry not in existing_entries:
                existing_entries.add(entry)
                new_count += 1

        with open("KnownNetworks.txt", "w") as f:
            for item in sorted(existing_entries):
                f.write(item + "\n")


        print(f"Scan complete. Added {new_count} new routers. Total unique: {len(existing_entries)}")
