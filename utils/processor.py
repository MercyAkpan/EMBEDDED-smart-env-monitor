# utils/processor.py
import numpy as np
history = []
MAX_HISTORY = 3

def normalize_scan(scan_results, golden_routers, min_rssi=-100):
    """
    scan_results: list of tuples (bssid, ssid, rssi)
    golden_routers: list of BSSIDs from loader.py
    """
    features = [0.0] * len(golden_routers)
    # Convert scan list to dictionary for O(1) lookup speed
    scan_dict = {res[0]: res[2] for res in scan_results}
    
    for i, bssid in enumerate(golden_routers):
        if bssid in scan_dict:
            rssi = scan_dict[bssid]
            # Normalization math (100 + rssi)
            if rssi > min_rssi:
                features[i] = float(100 + rssi)
            else:
                features[i] = 0.0
        else:
            features[i] = 0.0 # 2nd Else: Router not found
            
    return np.array(features, dtype=np.float32)


def get_smoothed_features(new_scan, golden_routers):
    """
    Implements Weighted Moving Average (WMA).
    """
    global history
    
    # 1. Normalize the incoming raw scan
    current_vector = normalize_scan(new_scan, golden_routers)
    
    # 2. Update History (Maintain the queue)
    history.append(current_vector)
    if len(history) > MAX_HISTORY:
        history.pop(0) # Remove oldest
        
    # 3. Apply Weights 
    # If 3 scans: Oldest gets 20%, Middle 30%, Newest 50% weight
    if len(history) == 3:
        weights = [0.2, 0.3, 0.5]
    elif len(history) == 2:
        weights = [0.4, 0.6]
    else:
        weights = [1.0]

    # 4. Calculate Weighted Average
    smoothed = np.zeros_like(current_vector)
    for i, vec in enumerate(history):
        smoothed += vec * weights[i]
        
    return smoothed
