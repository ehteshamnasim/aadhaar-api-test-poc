from flask import Flask, Response, send_from_directory
import json
import time
import threading
import queue

app = Flask(__name__, static_folder='.')

# Global queue for SSE events
event_queue = queue.Queue()

def send_event(event_type: str, data: dict):
    """Send event to all SSE clients"""
    event = {
        'type': event_type,
        **data
    }
    event_queue.put(event)

@app.route('/')
def index():
    """Serve dashboard HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def styles():
    """Serve CSS"""
    return send_from_directory('.', 'style.css')

@app.route('/app.js')
def scripts():
    """Serve JavaScript"""
    return send_from_directory('.', 'app.js')

@app.route('/events')
def stream():
    """Server-Sent Events endpoint"""
    def event_stream():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'status', 'message': 'Connected to dashboard'})}\n\n"
        
        while True:
            try:
                # Get event from queue (non-blocking)
                event = event_queue.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f": heartbeat\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')

def start_dashboard_server():
    """Start dashboard server in background"""
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

if __name__ == '__main__':
    print("Dashboard available at: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)