from flask import Flask, request, jsonify
import threading
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Global variable to store the latest scan data
latest_scan = None

# Dummy fingerprint database for localization.
fingerprints = [
    {"x": 2, "y": 2, "rssi": {
        "10:71:B3:FD:16:21": -50,
        "C0:25:E9:52:38:F2": -60,
        "80:7D:14:05:52:70": -80,
        "20:08:89:97:80:20": -85
    }},
    {"x": 8, "y": 2, "rssi": {
        "10:71:B3:FD:16:21": -65,
        "C0:25:E9:52:38:F2": -55,
        "80:7D:14:05:52:70": -90,
        "20:08:89:97:80:20": -88
    }},
    {"x": 2, "y": 8, "rssi": {
        "10:71:B3:FD:16:21": -70,
        "C0:25:E9:52:38:F2": -75,
        "80:7D:14:05:52:70": -50,
        "20:08:89:97:80:20": -60
    }},
    {"x": 8, "y": 8, "rssi": {
        "10:71:B3:FD:16:21": -80,
        "C0:25:E9:52:38:F2": -78,
        "80:7D:14:05:52:70": -60,
        "20:08:89:97:80:20": -40
    }}
]

# Automatically generate a list of known BSSIDs from the fingerprint database.
known_bssids = {bssid for fp in fingerprints for bssid in fp["rssi"]}

@app.route('/data', methods=['POST'])
def data():
    global latest_scan
    latest_scan = request.json
    print("Received scan data:", latest_scan)
    return jsonify({"status": "received"}), 200

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Start the Flask server in a separate thread.
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Set up matplotlib for real-time plotting.
plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Estimated Car Position')

# Static blue point at the specified position (3.53, 3.81)
blue_point, = ax.plot([3.53], [3.81], 'bo', markersize=8)  # Blue circle at (3.53, 3.81)

pos_plot, = ax.plot([], [], 'ro', markersize=10)  # Red dot for position

def estimate_position_knn(measured, fingerprints, k=3):
    """
    Estimate position using k-NN by comparing measured RSSI values with fingerprint database.
    """
    # Prepare training data (features and positions)
    X_train = []
    y_train = []

    for fp in fingerprints:
        rssi_values = list(fp["rssi"].values())
        X_train.append(rssi_values)
        y_train.append([fp["x"], fp["y"]])

    # Convert to numpy arrays
    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # Measure the RSSI values for known BSSIDs
    measured_values = [measured.get(bssid, None) for bssid in known_bssids]
    
    # Remove None values (those BSSIDs not in the scan)
    measured_values = [value for value in measured_values if value is not None]

    if len(measured_values) == 0:
        return None  # No common BSSIDs, cannot estimate position

    # Find the k-nearest neighbors
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='auto').fit(X_train)
    distances, indices = nbrs.kneighbors([measured_values])

    # Compute the weighted average of the k-nearest neighbors
    weighted_position = np.zeros(2)
    total_distance = 0

    for i, idx in enumerate(indices[0]):
        distance = distances[0][i]
        weighted_position += y_train[idx] / (distance + 1e-6)  # Avoid division by zero
        total_distance += 1 / (distance + 1e-6)

    weighted_position /= total_distance
    return tuple(weighted_position)

print("Server is running and waiting for ESP32 data...")

# Main loop for visualization.
while True:
    if latest_scan:
        measured = {net["bssid"]: net["rssi"] for net in latest_scan.get("networks", []) if net["bssid"] in known_bssids}

        print("Measured:", measured)
        pos = estimate_position_knn(measured, fingerprints)
        print("Estimated Position:", pos)

        if pos:
            x, y = pos
            pos_plot.set_data([x], [y])  # Convert to lists
            plt.draw()
            fig.canvas.flush_events()  # Ensures real-time updates
        
        latest_scan = None  # Clear data after processing
    
    plt.pause(0.5)  # Allow smooth updates
