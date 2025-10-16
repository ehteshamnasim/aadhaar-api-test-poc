// Connect to Server-Sent Events for real-time updates
const eventSource = new EventSource('/events');

// Update timestamp
function updateTimestamp() {
    const now = new Date().toLocaleTimeString();
    document.getElementById('timestamp').textContent = now;
}

// Add log entry
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Update coverage circle
function updateCoverage(percentage) {
    const circle = document.getElementById('coverage-circle');
    const text = document.getElementById('coverage-text');
    const circumference = 314; // 2 * PI * 50
    const offset = circumference - (percentage / 100) * circumference;
    
    circle.style.strokeDashoffset = offset;
    text.textContent = `${percentage}%`;
    
    // Change color based on threshold
    if (percentage >= 85) {
        circle.style.stroke = '#4caf50';
    } else if (percentage >= 70) {
        circle.style.stroke = '#ff9800';
    } else {
        circle.style.stroke = '#f44336';
    }
}

// Update badge status
function updateBadge(elementId, status) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.className = 'badge';
    
    if (status === 'success' || status === 'passed' || status === 'completed') {
        element.style.background = '#4caf50';
        element.style.color = 'white';
        element.textContent = '✓ Passed';
    } else if (status === 'failed' || status === 'error') {
        element.style.background = '#f44336';
        element.style.color = 'white';
        element.textContent = '✗ Failed';
    } else if (status === 'running' || status === 'in_progress') {
        element.style.background = '#2196f3';
        element.style.color = 'white';
        element.textContent = '⋯ Running';
    } else {
        element.style.background = '#e0e0e0';
        element.style.color = '#666';
        element.textContent = status || 'Pending';
    }
}

// Handle SSE events
// Handle SSE events
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateTimestamp();
    
    // Update based on event type
    switch(data.type) {
        case 'status':
            document.getElementById('status').textContent = data.message;
            addLog(data.message, 'info');
            break;
            
        case 'parse':
            document.getElementById('spec-file').textContent = data.file || 'specs/aadhaar-api.yaml';
            document.getElementById('endpoint-count').textContent = data.endpoints || 0;
            updateBadge('parse-status', 'success');
            addLog(`Parsed ${data.endpoints || 0} endpoints`, 'success');
            break;
            
        case 'generate':
            const progress = data.progress || 0;
            document.getElementById('gen-progress').style.width = progress + '%';
            document.getElementById('tests-generated').textContent = data.count || 0;
            updateBadge('gen-status', data.status || 'running');
            
            // Add detailed message to log
            if (data.message) {
                addLog(data.message, data.status === 'success' ? 'success' : 'info');
            }
            break;
            
        case 'validate':
            updateBadge('syntax-check', data.syntax ? 'success' : 'failed');
            updateBadge('import-check', data.imports ? 'success' : 'failed');
            updateBadge('validation-status', data.overall ? 'success' : 'failed');
            addLog(data.message, data.overall ? 'success' : 'error');
            break;
            
        case 'execute':
            document.getElementById('tests-passed').textContent = data.passed || 0;
            document.getElementById('tests-failed').textContent = data.failed || 0;
            document.getElementById('tests-total').textContent = data.total || 0;
            
            const statusText = data.status === 'running' ? 'Running...' : 
                             `${data.passed || 0}/${data.total || 0} passed`;
            addLog(`Tests: ${statusText}`, 
                   data.failed === 0 && data.status === 'completed' ? 'success' : 
                   data.status === 'running' ? 'info' : 'error');
            break;
            
        case 'coverage':
            const percentage = data.percentage || 0;
            updateCoverage(percentage);
            
            if (data.status === 'running') {
                addLog('Calculating coverage...', 'info');
            } else if (data.status === 'completed') {
                addLog(`Coverage: ${percentage}%`, percentage >= 85 ? 'success' : 'info');
            }
            break;
            
        case 'contract':
            document.getElementById('contracts-tested').textContent = data.total || 0;
            document.getElementById('contracts-passed').textContent = data.passed || 0;
            document.getElementById('contracts-failed').textContent = data.failed || 0;
            
            if (data.status === 'running') {
                addLog(`Running contract tests for ${data.total || 0} endpoints...`, 'info');
            } else if (data.status === 'completed') {
                addLog(`Contract tests: ${data.passed || 0}/${data.total || 0} passed`, 
                       data.failed === 0 ? 'success' : 'error');
            }
            break;
            
        case 'git':
            document.getElementById('git-repo').textContent = 'Initialized';
            updateBadge('git-commit', data.committed ? 'success' : 'pending');
            addLog(data.message, data.committed ? 'success' : 'info');
            break;
            
        case 'cicd':
            updateBadge('cicd-status', data.status);
            document.getElementById('build-status').textContent = data.build || '-';
            addLog(data.message, data.status === 'success' ? 'success' : 'info');
            break;
            
        case 'error':
            addLog(`Error: ${data.message}`, 'error');
            break;
    }
};

eventSource.onerror = function(error) {
    console.error('SSE Error:', error);
    document.getElementById('status').textContent = 'Connection lost';
    addLog('Connection to server lost. Retrying...', 'error');
};

// Initialize
updateTimestamp();
setInterval(updateTimestamp, 1000);
addLog('Dashboard initialized', 'info');