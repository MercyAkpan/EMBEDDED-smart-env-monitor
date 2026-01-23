import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier # Changed from LinearSVC
from sklearn.utils import shuffle # To handle the shuffling
import joblib
from sklearn.metrics import classification_report

def train_system():
    DATA_FOLDER = "training_zones"
    X = [] 
    y = [] 

    # --- BLOCK 1: DATA GATHERING ---
    if not os.path.exists(DATA_FOLDER):
        print("Error: No training_zones folder found!")
        return

    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".csv"):
            room_name = filename.replace(".csv", "")
            df = pd.read_csv(os.path.join(DATA_FOLDER, filename), header=None)
            
            X.extend(df.values.tolist())
            y.extend([room_name] * len(df))

    # --- BLOCK 2: MEMORY OPTIMIZATION ---
    # Strictly converting to float32 for Pi 3 RAM efficiency
    X_optimised = np.array(X, dtype=np.float32)
    y_optimised = np.array(y)

    X_optimised, y_optimised = shuffle(X_optimised, y_optimised, random_state=42)
    print(f"✅ Data Shuffled. Total samples: {len(X_optimised)}")

    # --- BLOCK 3: THE BRAIN BUILDING (LinearSVC) ---
    # dual=False makes it solve faster on the Pi's CPU

    model = RandomForestClassifier(
        n_estimators=50,      # Small number of trees = low RAM
        max_depth=5,          # Shallow trees = low RAM
        min_samples_leaf=3,   # Better generalization for noisy exhibition halls
        n_jobs=1,             # Single core to avoid RAM spikes
        random_state=42       # Reproducible results
    )
    
    print("🧠 Training Random Forest Model...")
    model.fit(X_optimised, y_optimised)

    predictions = model.predict(X_optimised)
    print("\n--- Map Quality Report ---")
    print(classification_report(y_optimised, predictions))

    # --- BLOCK 4: EXPORTING ---
    SAVE_NAME = "model2.joblib"
    joblib.dump(model, SAVE_NAME, compress=3)
    file_size = os.path.getsize(SAVE_NAME) / 1024
    print(f"Success: {SAVE_NAME} is ready. File size: ~{file_size:.1f} KB")

if __name__ == "__main__":
    train_system()
