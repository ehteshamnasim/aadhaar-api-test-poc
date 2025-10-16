#!/usr/bin/env python3
"""
Standalone dashboard server - runs independently
Keeps running and shows updates from all POC runs
"""

import sys
from pathlib import Path

# Add dashboard to path
sys.path.insert(0, str(Path(__file__).parent / 'dashboard'))

from server import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📊 AI Test Automation Dashboard")
    print("="*70)
    print("\n🌐 Dashboard running at: http://localhost:8080")
    print("   Keep this running to see live updates from POC runs")
    print("\n💡 Events received via HTTP POST to /api/event")
    print("   SSE stream available at /events")
    print("\n💡 Tip: In another terminal, commit spec changes to trigger POC")
    print("   The dashboard will show real-time progress updates")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    try:
        app.run(host='0.0.0.0', port=8090, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped\n")