from flask import Flask, request, jsonify
import json
import csv
import os
from collections import defaultdict
from scipy.spatial.distance import euclidean

app = Flask(__name__)
DATA_FILE = 'training_data.csv'

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
    
    # Filter out non-ESP32 networks (optional)
    esp32_networks = {bssid: rssi for bssid, rssi in scan_data.items() if bssid.startswith("ESP32_")}
    
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['location', 'scan_data'])
        writer.writerow([location, json.dumps(esp32_networks)])
    
    return jsonify({'status': 'success'})

@app.route('/locate', methods=['POST'])
def locate():
    current_scan = request.json
    training_data = load_training_data()
    
    if not training_data:
        return jsonify({'error': 'No training data available'}), 400
    
    all_bssids = get_all_bssids(training_data)
    
    # Filter current scan to include only ESP32 networks
    esp32_scan = {bssid: rssi for bssid, rssi in current_scan.items() if bssid.startswith("ESP32_")}
    
    current_vector = create_feature_vector(esp32_scan, all_bssids)
    
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
    votes = defaultdict(int)
    for d, loc in neighbors:
        votes[loc] += 1
    
    predicted_location = max(votes, key=votes.get)
    return jsonify({'location': predicted_location})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)