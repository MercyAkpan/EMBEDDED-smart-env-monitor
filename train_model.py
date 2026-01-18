import os
import numpy as np
import pandas as pd
from sklearn.svm import LinearSVC
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
    X_optimized = np.array(X, dtype=np.float32)
    y_optimized = np.array(y)

    # --- BLOCK 3: THE BRAIN BUILDING (LinearSVC) ---
    # dual=False makes it solve faster on the Pi's CPU
    model = LinearSVC(dual=False, max_iter=10000, tol=1e-4)
    model.fit(X_optimized, y_optimized)

    predictions = model.predict(X_optimized)
    print("\n--- Map Quality Report ---")
    print(classification_report(y_optimized, predictions))

    # --- BLOCK 4: EXPORTING ---
    joblib.dump(model, "model.joblib")
    print("Success: 'model.joblib' is ready.")

if __name__ == "__main__":
    train_system()
