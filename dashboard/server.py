from flask import Flask, Response, send_from_directory, request
from flask_cors import CORS
import json
import time
import queue
import threading
import os
from datetime import datetime


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

@app.route('/coverage-report')
def coverage_report():
    """Redirect to coverage HTML report"""
    return send_from_directory('../htmlcov', 'index.html')

@app.route('/coverage-report/<path:filename>')
def coverage_files(filename):
    """Serve coverage report static files"""
    return send_from_directory('../htmlcov', filename)

@app.route('/generated-tests')
def generated_tests():
    """Show generated tests - NO CACHE"""
    try:
        test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'test_aadhaar_api.py')
        
        if os.path.exists(test_file):
            # Read fresh content
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Get file stats
            stats = os.stat(test_file)
            modified_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            test_count = content.count('def test_')
            line_count = len(content.split('\n'))
            
            import html as html_module
            content_escaped = html_module.escape(content)
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Generated Tests</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #1e1e1e;
            font-family: 'Courier New', monospace;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #2d2d2d;
            padding: 20px;
            border-radius: 8px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #fff;
            margin: 0;
        }}
        .stats {{
            color: #888;
            font-size: 14px;
        }}
        .stats span {{
            display: inline-block;
            margin-left: 20px;
            color: #4caf50;
        }}
        pre {{
            margin: 0;
            border-radius: 4px;
            max-height: 80vh;
            overflow: auto;
        }}
        .back-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .back-btn:hover {{
            background: #764ba2;
        }}
        .refresh-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #4caf50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin-left: 10px;
            cursor: pointer;
        }}
        .refresh-btn:hover {{
            background: #45a049;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <a href="/" class="back-btn">← Back to Dashboard</a>
                <a href="/generated-tests" class="refresh-btn" onclick="location.reload()">🔄 Refresh</a>
            </div>
            <div class="stats">
                Last modified: <span>{modified_time}</span> |
                Test cases: <span>{test_count}</span> |
                Lines: <span>{line_count}</span>
            </div>
        </div>
        <h1>Generated Test File: test_aadhaar_api.py</h1>
        <pre><code class="language-python">{content_escaped}</code></pre>
    </div>
    <script>
        hljs.highlightAll();
        // Auto-refresh every 10 seconds when file changes
        setTimeout(function(){{
            fetch('/api/test-file-changed')
                .then(r => r.json())
                .then(data => {{
                    if (data.changed) {{
                        console.log('File changed, reloading...');
                        location.reload();
                    }}
                }});
        }}, 10000);
    </script>
</body>
</html>
"""
            return html, 200, {'Cache-Control': 'no-cache, no-store, must-revalidate'}
        else:
            return """
                <html>
                <head>
                    <meta http-equiv="refresh" content="5">
                </head>
                <body style="font-family: Arial; padding: 40px; text-align: center;">
                    <h1>⏳ Generating Tests...</h1>
                    <p>Page will auto-refresh when tests are ready</p>
                    <a href="/" style="color: #667eea; text-decoration: none;">← Back to Dashboard</a>
                </body>
                </html>
            """, 404
    except Exception as e:
        return f"<h1>Error: {e}</h1><a href='/'>Back</a>", 500

@app.route('/api/test-file-changed')
def test_file_changed():
    """Check if test file was modified recently"""
    try:
        test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'test_aadhaar_api.py')
        if os.path.exists(test_file):
            stats = os.stat(test_file)
            modified_time = stats.st_mtime
            current_time = time.time()
            changed = (current_time - modified_time) < 60  # Changed in last minute
            return {'changed': changed, 'modified': modified_time}, 200
        return {'changed': False}, 200
    except:
        return {'changed': False}, 200


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


