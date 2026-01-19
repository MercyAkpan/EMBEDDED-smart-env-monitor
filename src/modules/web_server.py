import os
import cv2
from flask import Flask, render_template, Response, jsonify
import queue
import threading
import socket
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
app = Flask(__name__,
template_folder=os.path.join(BASE_DIR, 'templates'),
static_folder=os.path.join(BASE_DIR, 'static'))


# Global cache to hold the latest reading for the dashboard
latest_data = {"temperature": 30, "humidity": 60, "C02Concentration": 300}

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()


def data_collector(sensor_queue):
    """Background thread to drain the sensor queue into a local variable"""
    global latest_data
    print(f"[WEB] In the data collector")
    while True:
        try:
            # Block for a short time to get data
            print(f"[WEB]")
            data = sensor_queue.get(timeout=1)
            latest_data = data
            while not sensor_queue.empty():
                latest_data = sensor_queue.get_nowait()
        except queue.Empty:
            continue

def generate_frames():
    """Camera Generator: Only runs when the user views the stream"""
    # For IP Camera, use 'http://admin:password@192.168.1.XX/video'
    # For USB/Pi Cam, use 0
    camera = cv2.VideoCapture(0) 
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Resize to save CPU for the AI and ESP32 tasks
            frame = cv2.resize(frame, (480, 360))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()

@app.route('/')
def index():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return str(e), 500 # This will show the actual error in your browser instead of just "500"

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/data')
def get_sensor_data():
    return jsonify(latest_data)

def run_web_process(sensor_queue):
    # Start the data collector thread
    print(f"[WEB] In the web process")
    t = threading.Thread(target=data_collector, args=(sensor_queue,), daemon=True)
    t.start()

    ip = get_ip_address()
    print(f"\n--- DASHBOARD LIVE AT http://{ip}:5000 ---\n")
    # Run the server
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
