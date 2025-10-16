from flask import Flask, Response, send_from_directory, request
from flask_cors import CORS
import json
import time
import queue
import threading

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS

# Global queue and history for events
event_queue = queue.Queue()
event_history = []
MAX_HISTORY = 100

# Lock for thread-safe operations
history_lock = threading.Lock()

def broadcast_event(event_type: str, data: dict):
    """Broadcast event to all connected clients"""
    event = {
        'type': event_type,
        'timestamp': time.time(),
        **data
    }
    
    # Add to queue
    event_queue.put(event)
    
    # Add to history (thread-safe)
    with history_lock:
        event_history.append(event)
        if len(event_history) > MAX_HISTORY:
            event_history.pop(0)
    
    # Log for debugging
    print(f"[Dashboard] 📡 Broadcast: {event_type} - {data}")
    return True

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def styles():
    return send_from_directory('.', 'style.css')

@app.route('/app.js')
def scripts():
    return send_from_directory('.', 'app.js')

@app.route('/api/event', methods=['POST', 'OPTIONS'])
def receive_event():
    """Receive events from main.py"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        if not data:
            return {'status': 'error', 'message': 'No data provided'}, 400
        
        event_type = data.pop('type', 'status')
        success = broadcast_event(event_type, data)
        
        if success:
            return {'status': 'ok'}, 200
        else:
            return {'status': 'error', 'message': 'Failed to broadcast'}, 500
            
    except Exception as e:
        print(f"[Dashboard] ❌ Error: {e}")
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/events')
def stream():
    """Server-Sent Events stream"""
    def event_stream():
        # Send connection message
        connection_msg = {
            'type': 'connected',
            'message': 'Dashboard connected',
            'timestamp': time.time()
        }
        yield f"data: {json.dumps(connection_msg)}\n\n"
        print("[Dashboard] 🔗 Client connected to SSE")
        
        # Send recent history
        with history_lock:
            recent = event_history[-20:] if event_history else []
        
        for event in recent:
            yield f"data: {json.dumps(event)}\n\n"
        
        # Stream new events
        last_heartbeat = time.time()
        while True:
            try:
                event = event_queue.get(timeout=1)
                yield f"data: {json.dumps(event)}\n\n"
                last_heartbeat = time.time()
            except queue.Empty:
                # Heartbeat every 15 seconds
                if time.time() - last_heartbeat > 15:
                    yield f": heartbeat\n\n"
                    last_heartbeat = time.time()
    
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    with history_lock:
        history_count = len(event_history)
    
    return {
        'status': 'ok',
        'queue_size': event_queue.qsize(),
        'history_size': history_count,
        'timestamp': time.time()
    }, 200

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📊 AI Test Automation Dashboard")
    print("="*70)
    print("\n🌐 Dashboard: http://localhost:8080")
    print("📡 SSE Stream: http://localhost:8080/events")
    print("📨 Event API: POST http://localhost:8080/api/event")
    print("💚 Health: http://localhost:8080/api/health")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)