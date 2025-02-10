from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Dictionary to store fixed node positions (using node id as key)
fixed_nodes = {}

# Dictionary to store the latest mobile node position
mobile_node = {"x": None, "y": None}

@app.route('/fixed', methods=['POST'])
def update_fixed():
    data = request.get_json()
    if not data:
        return "No data provided", 400
    node_id = data.get("id")
    x = data.get("x")
    y = data.get("y")
    if node_id is None or x is None or y is None:
        return "Missing data", 400
    fixed_nodes[node_id] = {"x": x, "y": y}
    return jsonify({"status": "Fixed node updated", "node": node_id})

@app.route('/mobile', methods=['POST'])
def update_mobile():
    data = request.get_json()
    if not data:
        return "No data provided", 400
    x = data.get("x")
    y = data.get("y")
    if x is None or y is None:
        return "Missing data", 400
    mobile_node["x"] = x
    mobile_node["y"] = y
    return jsonify({"status": "Mobile node updated"})

# This endpoint returns the latest positions as JSON.
@app.route('/data', methods=['GET'])
def data():
    return jsonify({
        "fixed_nodes": fixed_nodes,
        "mobile_node": mobile_node
    })

# The main page that shows the visualization.
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) at port 5000.
    app.run(host='0.0.0.0', port=5000, debug=True)
