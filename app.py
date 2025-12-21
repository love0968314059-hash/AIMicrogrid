"""
Flask Web Application for Microgrid Digital Twin System
Provides REST API and serves 3D visualization interface
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from digital_twin import DigitalTwin
from nlp_interface import NLPInterface
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global digital twin instance
digital_twin = None
nlp_interface = None
simulation_thread = None
running = False


def initialize_system():
    """Initialize the digital twin system"""
    global digital_twin, nlp_interface
    digital_twin = DigitalTwin()
    digital_twin.initialize()
    nlp_interface = NLPInterface(digital_twin)
    print("System initialized!")


def run_simulation():
    """Run continuous simulation"""
    global running, digital_twin
    while running:
        if digital_twin:
            digital_twin.step()
        time.sleep(1.0)  # 1 second per hour simulation


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    if not digital_twin:
        return jsonify({'error': 'System not initialized'}), 500
    
    status = digital_twin.get_status()
    return jsonify(status)


@app.route('/api/step', methods=['POST'])
def step():
    """Execute one simulation step"""
    if not digital_twin:
        return jsonify({'error': 'System not initialized'}), 500
    
    data = request.json or {}
    action = data.get('action')
    
    result = digital_twin.step(action)
    return jsonify(result)


@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """Evaluate energy management strategy"""
    if not digital_twin:
        return jsonify({'error': 'System not initialized'}), 500
    
    data = request.json or {}
    strategy = data.get('strategy', 'rl')
    horizon = data.get('horizon', 24)
    
    result = digital_twin.evaluate_strategy(horizon=horizon, strategy=strategy)
    return jsonify(result)


@app.route('/api/predict', methods=['GET'])
def predict():
    """Get predictions"""
    if not digital_twin:
        return jsonify({'error': 'System not initialized'}), 500
    
    horizon = request.args.get('horizon', 24, type=int)
    predictions = digital_twin.prediction_system.predict_horizon(
        start_hour=digital_twin.current_time.hour,
        horizon=min(horizon, 24)
    )
    return jsonify(predictions)


@app.route('/api/nlp', methods=['POST'])
def nlp_query():
    """Process natural language query"""
    if not nlp_interface:
        return jsonify({'error': 'NLP interface not initialized'}), 500
    
    data = request.json or {}
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    response = nlp_interface.process_query(query)
    return jsonify({'response': response})


@app.route('/api/control', methods=['POST'])
def control():
    """Control simulation"""
    global running, simulation_thread
    
    data = request.json or {}
    action = data.get('action')
    
    if action == 'start':
        if not running:
            running = True
            simulation_thread = threading.Thread(target=run_simulation, daemon=True)
            simulation_thread.start()
            return jsonify({'status': 'started'})
    elif action == 'stop':
        running = False
        return jsonify({'status': 'stopped'})
    elif action == 'reset':
        running = False
        if digital_twin:
            digital_twin.reset()
        return jsonify({'status': 'reset'})
    
    return jsonify({'status': 'unknown_action'}), 400


if __name__ == '__main__':
    print("Initializing Microgrid Digital Twin System...")
    initialize_system()
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
