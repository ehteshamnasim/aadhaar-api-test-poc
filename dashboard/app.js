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
    element.className = 'badge';
    
    if (status === 'success' || status === 'passed') {
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
        element.textContent = status;
    }
}

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
            document.getElementById('spec-file').textContent = data.file;
            document.getElementById('endpoint-count').textContent = data.endpoints;
            updateBadge('parse-status', 'success');
            addLog(`Parsed ${data.endpoints} endpoints`, 'success');
            break;
            
        case 'generate':
            document.getElementById('gen-progress').style.width = data.progress + '%';
            document.getElementById('tests-generated').textContent = data.count;
            updateBadge('gen-status', data.status);
            addLog(data.message, 'success');
            break;
            
        case 'validate':
            updateBadge('syntax-check', data.syntax ? 'success' : 'failed');
            updateBadge('import-check', data.imports ? 'success' : 'failed');
            updateBadge('validation-status', data.overall ? 'success' : 'failed');
            addLog(data.message, data.overall ? 'success' : 'error');
            break;
            
        case 'execute':
            document.getElementById('tests-passed').textContent = data.passed;
            document.getElementById('tests-failed').textContent = data.failed;
            document.getElementById('tests-total').textContent = data.total;
            addLog(`Tests: ${data.passed}/${data.total} passed`, data.failed === 0 ? 'success' : 'error');
            break;
            
        case 'coverage':
            updateCoverage(data.percentage);
            addLog(`Coverage: ${data.percentage}%`, data.percentage >= 85 ? 'success' : 'info');
            break;
            
        case 'contract':
            document.getElementById('contracts-tested').textContent = data.total;
            document.getElementById('contracts-passed').textContent = data.passed;
            document.getElementById('contracts-failed').textContent = data.failed;
            addLog(`Contract tests: ${data.passed}/${data.total} passed`, data.failed === 0 ? 'success' : 'error');
            break;
            
        case 'git':
            document.getElementById('git-repo').textContent = 'Initialized';
            updateBadge('git-commit', data.committed ? 'success' : 'pending');
            addLog(data.message, 'success');
            break;
            
        case 'cicd':
            updateBadge('cicd-status', data.status);
            document.getElementById('build-status').textContent = data.build;
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