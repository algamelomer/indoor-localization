import json
import csv
import os
import time
import requests
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from flask import Flask, request, jsonify
from collections import defaultdict
from scipy.spatial.distance import euclidean

global estimated_x, estimated_y
estimated_x, estimated_y = None, None
app = Flask(__name__)
DATA_FILE = 'training_data.csv'
SERVER_URL = 'http://127.0.0.1:5000/locate'  # Change if hosted elsewhere
ESP_SCAN_URL = 'http://192.168.1.100/scan'  # Change to ESP IP

def load_training_data():
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    'location': row['location'],
                    'scan': json.loads(row['scan_data'])
                })
    return data

def get_all_bssids(data):
    bssids = set()
    for entry in data:
        bssids.update(entry['scan'].keys())
    return sorted(bssids)

def create_feature_vector(scan, all_bssids, default_rssi=-100):
    return [scan.get(bssid, default_rssi) for bssid in all_bssids]

@app.route('/train', methods=['POST'])
def train():
    data = request.json
    location = data['location']
    scan_data = data['scan_data']
    
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['location', 'scan_data'])
        writer.writerow([location, json.dumps(scan_data)])
    
    return jsonify({'status': 'success'})

@app.route('/locate', methods=['POST'])
def locate():
    global estimated_x, estimated_y 
    current_scan = request.json
    training_data = load_training_data()
    
    if not training_data:
        return jsonify({'error': 'No training data available'}), 400
    
    all_bssids = get_all_bssids(training_data)
    current_vector = create_feature_vector(current_scan, all_bssids)
    
    distances = []
    for entry in training_data:
        train_vector = create_feature_vector(entry['scan'], all_bssids)
        dist = euclidean(current_vector, train_vector)
        distances.append((dist, entry['location']))
    
    # Find k-nearest neighbors (k=3)
    k = 3
    distances.sort()
    neighbors = distances[:k]
    
    # Majority vote
# Weighted average position estimation
    weighted_x, weighted_y, total_weight = 0, 0, 0
    for dist, loc in neighbors:
        if dist == 0:
            return jsonify({'location': loc})  # Exact match
        x, y = location_map[loc]  # Get saved coordinates
        weight = 1 / dist  # Inverse distance weighting
        weighted_x += x * weight
        weighted_y += y * weight
        total_weight += weight

    # Compute weighted average position
    estimated_x = weighted_x / total_weight
    estimated_y = weighted_y / total_weight

    return jsonify({'location': f"Interpolated_{estimated_x:.2f}_{estimated_y:.2f}", 'x': estimated_x, 'y': estimated_y})

    # return jsonify({'location': predicted_location})

# Visualization Setup
training_data = load_training_data()
saved_locations = list(set(entry['location'] for entry in training_data))
location_map = {loc: (i, len(saved_locations) - i) for i, loc in enumerate(saved_locations)}

def get_current_location():
    try:
        esp_response = requests.get(ESP_SCAN_URL, timeout=2)
        if esp_response.status_code == 200:
            scan_data = esp_response.json()
            response = requests.post(SERVER_URL, json={"scan_data": scan_data})
            if response.status_code == 200:
                return response.json().get('location')
    except requests.exceptions.RequestException:
        return None
    return None

def update_plot(frame):
    global estimated_x, estimated_y 
    ax.clear()
    
    # Plot saved locations (Blue)
    for loc, (x, y) in location_map.items():
        ax.scatter(x, y, color='blue', label='Saved Locations' if loc == saved_locations[0] else "")
        ax.text(x, y, loc, fontsize=12, ha='right')

    # Get current location from ESP
    current_location = get_current_location()
    print(f"ESP Reported Location: {current_location}")  # Debugging

    if estimated_y or estimated_x:
            x = estimated_x
            y = estimated_x
    else:
        # Estimate position: find closest saved location
        closest_loc = min(location_map.keys(), key=lambda loc: abs(int(loc) - int(current_location)))
        x, y = location_map[closest_loc]
        print(f"Estimated Position: {x}, {y} (Closest to {closest_loc})")

    ax.scatter(x, y, color='red', label='Current Position')

    ax.legend()
    ax.set_title("Live Localization")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_ylim(0, len(saved_locations))
    ax.set_xlim(-1, len(saved_locations))


def run_flask():
    app.run(host='0.0.0.0', port=5000)

fig, ax = plt.subplots()
ani = FuncAnimation(fig, update_plot, interval=2000)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    plt.show()
