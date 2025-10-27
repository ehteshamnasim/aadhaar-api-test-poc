# Enhanced Dashboard Usage Guide

## Overview

The enhanced dashboard provides a comprehensive real-time view of all API testing features with a modern, tabbed interface.

## Features

### 1. **Overview Tab**
- Real-time statistics and metrics
- API specification status
- Test generation progress
- Test execution results
- Coverage information
- Activity log showing recent events

### 2. **Self-Healing Tab**
- Total healings performed
- Success rate percentage
- Average confidence score
- List of healing operations with:
  - Test name
  - Confidence score with visual bar
  - Timestamp
  - Status (Applied/Needs Review)
- Click any healing to view before/after code diff

### 3. **Error Analysis Tab**
- Total errors detected
- Unique error types count
- Error list with:
  - Error type and message
  - Root cause analysis
  - Timestamp
- Click any error to view:
  - Full error details
  - Request/response information
  - Fix suggestions

### 4. **API Diff Tab**
- Breaking changes count (red)
- Non-breaking changes count (green)
- Total changes
- Change list showing:
  - Change type (Added/Removed/Modified)
  - Affected endpoint/path
  - Description
  - Recommendations

### 5. **Anomalies Tab**
- Charts showing trends (placeholder for Chart.js)
- Anomaly list with:
  - Severity level (Critical/High/Medium)
  - Endpoint affected
  - Expected vs actual values
  - Description
  - Timestamp

### 6. **Traffic Replay Tab**
- Recording controls
- Traffic list showing:
  - HTTP method
  - URL
  - Status code
  - Timestamp
- Color-coded by method (GET/POST/PUT/DELETE)
- Automatic limit to last 100 requests

## How to Use

### Starting the Dashboard

1. Ensure backend is running:
```bash
python main.py --spec path/to/spec.yaml --dashboard
```

2. Open browser to: `http://localhost:5050`

3. The dashboard will automatically connect via Server-Sent Events (SSE)

### Navigation

- Click any tab button to switch views
- Badges show real-time counts for:
  - Healings performed
  - Errors detected
  - Changes found
  - Anomalies detected
  - Traffic recorded

### Interactive Elements

**Self-Healing:**
- Click a healing item to view the code diff
- Diff shows before (original) and after (healed) code side-by-side
- Red lines show removals, green lines show additions

**Error Analysis:**
- Click an error to view full details
- See request/response data
- Get actionable fix suggestions

**API Diff:**
- Breaking changes highlighted in red
- Non-breaking changes in green
- Each change includes impact assessment

**Anomalies:**
- Sorted by severity (Critical → Medium)
- Shows deviation from baseline
- Includes expected vs actual values

**Traffic Replay:**
- Shows live captured traffic
- Color-coded by status (success/error)
- Auto-scrolls to latest requests

### Real-Time Updates

All data updates automatically through SSE:
- No page refresh needed
- Live activity log
- Instant badge updates
- Smooth animations for new items

## File Structure

```
dashboard/
├── index-enhanced.html    # Main HTML structure
├── enhanced-style.css     # Modern styling
├── enhanced-app.js        # Event handling and updates
└── server.py             # Flask server (needs update)
```

## Next Steps

To fully integrate the enhanced dashboard:

1. **Update server.py** to handle new event types:
   - `healing`
   - `error_analysis`
   - `api_diff`
   - `anomaly`
   - `traffic`

2. **Integrate with main.py** to send these events:
```python
# In POCOrchestrator
dashboard.send_event('healing', healing_data)
dashboard.send_event('error_analysis', error_data)
# etc.
```

3. **Run demo** to see features in action:
```bash
python demo_features.py
```

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires:
- JavaScript enabled
- EventSource API support (all modern browsers)

## Performance

- Efficient rendering with minimal DOM manipulation
- Automatic cleanup (max 50 activity log entries, 100 traffic items)
- Smooth animations without blocking
- Lightweight (no heavy frameworks)

## Customization

### Colors
Edit `enhanced-style.css` variables:
```css
:root {
    --primary: #4F46E5;      /* Main color */
    --success: #22c55e;       /* Success/green */
    --warning: #f59e0b;       /* Warning/yellow */
    --error: #ef4444;         /* Error/red */
}
```

### Layout
Adjust grid columns in CSS:
```css
.grid-3 { grid-template-columns: repeat(3, 1fr); }
```

### Event Handling
Modify event handlers in `enhanced-app.js`:
```javascript
function handleHealing(event) {
    // Custom logic here
}
```

## Troubleshooting

**Dashboard not updating:**
- Check browser console for SSE errors
- Verify server.py is running on port 5050
- Ensure `/events` endpoint is accessible

**Styles not loading:**
- Clear browser cache
- Check file paths in index-enhanced.html
- Verify enhanced-style.css exists

**Events not appearing:**
- Confirm backend is sending events
- Check event names match (case-sensitive)
- Verify JSON format in event.data

## Demo Mode

For a cool demo presentation:

1. Run `demo_features.py` in background
2. Open dashboard in fullscreen (F11)
3. Switch between tabs to show features
4. Click items to show details
5. Watch real-time updates

## Tips

- **Self-Healing**: Look for high confidence scores (80%+)
- **Error Analysis**: Focus on fix suggestions for quick resolution
- **API Diff**: Filter by breaking changes first
- **Anomalies**: Sort by severity to prioritize issues
- **Traffic**: Use for debugging and test generation

## What Makes This Cool

✨ **Real-time**: No refresh needed, instant updates
🎨 **Modern Design**: Clean, dark theme with smooth animations
📊 **Comprehensive**: All features in one dashboard
🔍 **Interactive**: Click for details, hover for info
📱 **Responsive**: Works on desktop, tablet, and mobile
⚡ **Fast**: Efficient rendering, no lag
🎯 **Focused**: Each tab serves specific purpose
💡 **Informative**: Empty states guide users

Perfect for demos and production monitoring!
