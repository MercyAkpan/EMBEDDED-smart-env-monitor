# utils/loader.py
def load_golden_routers(filepath="Scan_Wifi/KnownNetworks.txt"):
    golden_bssids = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                # Extracts BSSID from "BSSID:XX:XX..., SSID:Name"
                bssid = line.split(",")[0].replace("BSSID:", "").strip()
                if bssid:
                    golden_bssids.append(bssid)
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
    return golden_bssids

GOLDEN_ROUTERS = load_golden_routers()
