from flask import Flask, Response, send_from_directory, request
from flask_cors import CORS
import json
import time
import queue
import threading
import os
from datetime import datetime
import re


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
    response = send_from_directory('.', 'index.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/style.css')
def styles():
    response = send_from_directory('.', 'style.css')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/app.js')
def scripts():
    response = send_from_directory('.', 'app.js')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

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
    """Serve coverage report with proper styling"""
    try:
        htmlcov_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'htmlcov')
        index_path = os.path.join(htmlcov_path, 'index.html')
        
        if os.path.exists(index_path):
            # Read and serve with cache control
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Inject custom styling to fix broken UI
            custom_css = """
            <style>
            body { font-family: Arial, sans-serif !important; }
            #header { background: #667eea !important; padding: 20px !important; }
            #header h1 { color: white !important; }
            table { width: 100% !important; border-collapse: collapse !important; }
            table th { background: #764ba2 !important; color: white !important; padding: 10px !important; }
            table td { padding: 8px !important; border-bottom: 1px solid #ddd !important; }
            .pc_cov { font-weight: bold !important; }
            </style>
            """
            
            # Inject before </head>
            if '</head>' in content:
                content = content.replace('</head>', custom_css + '</head>')
            
            response = app.response_class(
                response=content,
                status=200,
                mimetype='text/html'
            )
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        else:
            return """
                <html>
                <head>
                    <style>
                        body { font-family: Arial; padding: 40px; text-align: center; background: #f5f5f5; }
                        .container { background: white; padding: 40px; border-radius: 10px; max-width: 600px; margin: 0 auto; }
                        h1 { color: #667eea; }
                        a { color: #667eea; text-decoration: none; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>⚠️ Coverage Report Not Generated Yet</h1>
                        <p>Run POC first to generate coverage report</p>
                        <p><a href="/">← Back to Dashboard</a></p>
                    </div>
                </body>
                </html>
            """, 404
    except Exception as e:
        return f"""
            <html>
            <body style="font-family: Arial; padding: 40px; text-align: center;">
                <h1>Error Loading Coverage Report</h1>
                <p>{str(e)}</p>
                <a href="/">← Back to Dashboard</a>
            </body>
            </html>
        """, 500

@app.route('/coverage-report/<path:filename>')
def coverage_files(filename):
    """Serve coverage report static files"""
    return send_from_directory('../htmlcov', filename)

@app.route('/generated-tests')
def generated_tests():
    """Show latest generated test file"""
    try:
        tests_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')
        
        # Find all test files
        test_files = []
        for file in os.listdir(tests_dir):
            if file.startswith('test_aadhaar_api') and file.endswith('.py'):
                full_path = os.path.join(tests_dir, file)
                stats = os.stat(full_path)
                test_files.append({
                    'name': file,
                    'path': full_path,
                    'modified': stats.st_mtime
                })
        
        if not test_files:
            return """
                <html>
                <head>
                    <meta http-equiv="refresh" content="5">
                    <style>
                        body { font-family: Arial; padding: 40px; text-align: center; background: #f5f5f5; }
                        .container { background: white; padding: 40px; border-radius: 10px; max-width: 600px; margin: 0 auto; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>⏳ Generating Tests...</h1>
                        <p>Page will auto-refresh when tests are ready</p>
                        <a href="/">← Back to Dashboard</a>
                    </div>
                </body>
                </html>
            """, 404
        
        # Sort by modification time (latest first)
        test_files.sort(key=lambda x: x['modified'], reverse=True)
        latest_file = test_files[0]
        
        # Read content
        with open(latest_file['path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get stats
        modified_time = datetime.fromtimestamp(latest_file['modified']).strftime('%Y-%m-%d %H:%M:%S')
        test_count = content.count('def test_')
        line_count = len(content.split('\n'))
        
        # Extract version from filename
        version_match = re.search(r'_v(\d+)\.py$', latest_file['name'])
        version = f"v{version_match.group(1)}" if version_match else "v1"
        
        import html as html_module
        content_escaped = html_module.escape(content)
        
        # Create file list dropdown
        file_options = ''
        for file in test_files:
            selected = 'selected' if file['name'] == latest_file['name'] else ''
            file_options += f'<option value="{file["name"]}" {selected}>{file["name"]}</option>'
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Generated Tests - {latest_file['name']}</title>
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
            max-width: 1400px;
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
            flex-wrap: wrap;
            gap: 15px;
        }}
        .header-left {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .header-right {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        h1 {{
            color: #fff;
            margin: 0;
            font-size: 24px;
        }}
        .version-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }}
        .stats {{
            background: #1e1e1e;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            color: #888;
            font-size: 14px;
        }}
        .stat-item span {{
            color: #4caf50;
            font-weight: bold;
            margin-left: 8px;
        }}
        .file-selector {{
            background: #1e1e1e;
            color: white;
            border: 1px solid #667eea;
            padding: 8px 16px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            cursor: pointer;
        }}
        .file-selector:hover {{
            background: #2d2d2d;
        }}
        pre {{
            margin: 0;
            border-radius: 4px;
            max-height: 75vh;
            overflow: auto;
        }}
        .back-btn, .refresh-btn, .download-btn {{
            display: inline-block;
            padding: 10px 20px;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .back-btn {{
            background: #667eea;
        }}
        .back-btn:hover {{
            background: #764ba2;
        }}
        .refresh-btn {{
            background: #4caf50;
            cursor: pointer;
        }}
        .refresh-btn:hover {{
            background: #45a049;
        }}
        .download-btn {{
            background: #ff9800;
        }}
        .download-btn:hover {{
            background: #f57c00;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <h1>Generated Test File</h1>
                <span class="version-badge">{version}</span>
            </div>
            <div class="header-right">
                <select class="file-selector" onchange="window.location.href='/generated-tests?file=' + this.value">
                    {file_options}
                </select>
                <a href="/" class="back-btn">← Dashboard</a>
                <a href="/generated-tests" class="refresh-btn" onclick="location.reload(); return false;">🔄 Refresh</a>
                <a href="/download-test/{latest_file['name']}" class="download-btn">⬇ Download</a>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                📄 File: <span>{latest_file['name']}</span>
            </div>
            <div class="stat-item">
                📅 Modified: <span>{modified_time}</span>
            </div>
            <div class="stat-item">
                🧪 Test Cases: <span>{test_count}</span>
            </div>
            <div class="stat-item">
                📏 Lines: <span>{line_count}</span>
            </div>
        </div>
        
        <pre><code class="language-python">{content_escaped}</code></pre>
    </div>
    <script>
        hljs.highlightAll();
    </script>
</body>
</html>
"""
        return html_content, 200, {'Cache-Control': 'no-cache, no-store, must-revalidate'}
    except Exception as e:
        return f"""
            <html>
            <body style="font-family: Arial; padding: 40px; text-align: center;">
                <h1>Error Loading Tests</h1>
                <p>{str(e)}</p>
                <a href="/">← Back to Dashboard</a>
            </body>
            </html>
        """, 500

@app.route('/download-test/<filename>')
def download_test(filename):
    """Download test file"""
    try:
        tests_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')
        return send_from_directory(tests_dir, filename, as_attachment=True)
    except Exception as e:
        return f"Error: {e}", 404

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


