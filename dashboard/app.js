// SSE Connection with auto-reconnect
let eventSource = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Update timestamp
function updateTimestamp() {
    const now = new Date().toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    document.getElementById('timestamp').textContent = now;
}

// Add log entry
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    // Format timestamp
    const timestamp = new Date().toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    entry.textContent = `[${timestamp}] ${message}`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Update coverage circle
function updateCoverage(percentage) {
    const circle = document.getElementById('coverage-circle');
    const text = document.getElementById('coverage-text');
    const circumference = 220; // 2 * π * 35
    const offset = circumference - (percentage / 100) * circumference;
    
    circle.style.strokeDashoffset = offset;
    text.textContent = `${percentage}%`;
    
    // Color based on percentage
    if (percentage >= 85) {
        circle.style.stroke = 'var(--success)';
        text.style.color = 'var(--success)';
    } else if (percentage >= 70) {
        circle.style.stroke = 'var(--warning)';
        text.style.color = 'var(--warning)';
    } else {
        circle.style.stroke = 'var(--primary)';
        text.style.color = 'var(--primary)';
    }
}

// Update badge with cleaner styling
function updateBadge(elementId, status) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Remove all previous badge classes
    element.className = element.className.replace(/badge-\w+/g, '').trim();
    
    switch(status) {
        case 'success':
        case 'passed':
        case 'completed':
            element.classList.add('badge-success');
            element.textContent = '✓ Passed';
            break;
        case 'failed':
        case 'error':
            element.classList.add('badge-error');
            element.textContent = '✗ Failed';
            break;
        case 'running':
        case 'in_progress':
            element.classList.add('badge-info');
            element.textContent = '● Running';
            break;
        case 'triggered':
            element.classList.add('badge-warning');
            element.textContent = '→ Triggered';
            break;
        default:
            element.classList.add('badge-pending');
            element.textContent = status || 'Pending';
    }
}

// Update status indicator
function updateStatusIndicator(status) {
    const statusElement = document.getElementById('status');
    const statusDot = document.querySelector('.status-dot');
    
    statusElement.textContent = status;
    
    if (status.includes('Connected')) {
        statusDot.style.background = 'var(--success)';
    } else if (status.includes('Error') || status.includes('Failed')) {
        statusDot.style.background = 'var(--error)';
    } else if (status.includes('Running') || status.includes('Processing')) {
        statusDot.style.background = 'var(--warning)';
    } else {
        statusDot.style.background = 'var(--gray-400)';
    }
}

// Reset dashboard
function resetDashboard() {
    if (!confirm('Reset dashboard? This will clear all current data.')) {
        return;
    }
    
    // Reset all values
    document.getElementById('spec-file').textContent = '-';
    document.getElementById('endpoint-count').textContent = '0';
    document.getElementById('tests-generated').textContent = '0';
    document.getElementById('tests-passed').textContent = '0';
    document.getElementById('tests-failed').textContent = '0';
    document.getElementById('tests-total').textContent = '0';
    document.getElementById('contracts-tested').textContent = '0';
    document.getElementById('contracts-passed').textContent = '0';
    document.getElementById('contracts-failed').textContent = '0';
    document.getElementById('git-repo').textContent = '-';
    document.getElementById('build-status').textContent = '-';
    
    // Reset all badges
    updateBadge('parse-status', 'Pending');
    updateBadge('gen-status', 'Pending');
    updateBadge('syntax-check', '-');
    updateBadge('import-check', '-');
    updateBadge('validation-status', 'Pending');
    updateBadge('git-commit', 'Pending');
    updateBadge('git-push', 'Pending');
    updateBadge('cicd-status', 'Not Started');
    
    // Reset progress and coverage
    document.getElementById('gen-progress').style.width = '0%';
    updateCoverage(0);
    
    // Hide sections
    document.getElementById('comparison-section').style.display = 'none';
    document.getElementById('coverage-btn').style.display = 'none';
    document.getElementById('tests-btn').style.display = 'none';
    
    // Clear logs and test results
    document.getElementById('log').innerHTML = '';
    document.getElementById('test-details-list').innerHTML = `
        <div class="empty-state">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <p>No test results yet</p>
        </div>
    `;
    
    updateStatusIndicator('Dashboard reset');
    addLog('Dashboard reset - ready for new POC run', 'info');
}

// Handle SSE events
function connectSSE() {
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource('/events');
    
    eventSource.onopen = function() {
        reconnectAttempts = 0;
        updateStatusIndicator('Connected - Ready');
        console.log('✅ SSE Connected');
    };

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateTimestamp();
        
        switch(data.type) {
            case 'connected':
                addLog('Connected to dashboard', 'info');
                break;
                
            case 'clear':
                document.getElementById('coverage-btn').style.display = 'none';
                document.getElementById('tests-btn').style.display = 'none';
                addLog('Starting new POC run...', 'info');
                break;
                
            case 'status':
                updateStatusIndicator(data.message);
                addLog(data.message, 'info');
                break;
                
            case 'parse':
                document.getElementById('spec-file').textContent = data.file || 'specs/aadhaar-api.yaml';
                document.getElementById('endpoint-count').textContent = data.endpoints || 0;
                updateBadge('parse-status', 'success');
                addLog(`Discovered ${data.endpoints || 0} API endpoints ready for test generation`, 'success');
                break;
            
            case 'test_created':
                const testNum = data.test_number;
                const testName = data.test_name;
                document.getElementById('tests-generated').textContent = testNum;
                addLog(`Test ${testNum}: ${testName}`, 'info');
                break;
                
            case 'generate':
                const progress = data.progress || 0;
                document.getElementById('gen-progress').style.width = progress + '%';
                
                if (data.count > 0) {
                    document.getElementById('tests-generated').textContent = data.count;
                }
                
                updateBadge('gen-status', data.status || 'running');
                
                if (data.message) {
                    addLog(data.message, data.status === 'success' ? 'success' : 'info');
                }
                
                if (data.status === 'success' && data.count > 0) {
                    document.getElementById('tests-btn').style.display = 'inline-flex';
                    addLog('Test generation complete - test file is ready for review', 'success');
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
                
                const statusText = `Executed ${data.total || 0} tests: ${data.passed || 0} passed, ${data.failed || 0} failed`;
                addLog(statusText, data.failed === 0 ? 'success' : 'error');
                
                // Update test details panel
                if (data.details && data.details.length > 0) {
                    const detailsList = document.getElementById('test-details-list');
                    detailsList.innerHTML = '';
                    
                    data.details.forEach((detail) => {
                        const detailDiv = document.createElement('div');
                        detailDiv.className = detail.passed ? 'test-detail-item passed' : 'test-detail-item failed';
                        
                        detailDiv.innerHTML = `
                            <span class="test-name">${detail.name}</span>
                            <div class="test-reason">${detail.reason}</div>
                        `;
                        detailsList.appendChild(detailDiv);
                    });
                }
                break;
                
            case 'coverage':
                const percentage = data.percentage || 0;
                updateCoverage(percentage);
                addLog(`Code coverage analysis complete: ${percentage}%`, percentage >= 85 ? 'success' : 'info');
                
                if (percentage > 0) {
                    document.getElementById('coverage-btn').style.display = 'inline-flex';
                    addLog('Coverage report generated successfully and ready for review', 'success');
                }
                break;
                
            case 'contract':
                document.getElementById('contracts-tested').textContent = data.total || 0;
                document.getElementById('contracts-passed').textContent = data.passed || 0;
                document.getElementById('contracts-failed').textContent = data.failed || 0;
                
                if (data.status === 'completed') {
                    addLog(`Contract tests: ${data.passed || 0}/${data.total || 0} passed`, 
                           data.failed === 0 ? 'success' : 'error');
                }
                break;
                
            case 'git':
                document.getElementById('git-repo').textContent = 'Initialized';
                updateBadge('git-commit', data.committed ? 'success' : 'pending');
                updateBadge('git-push', data.pushed ? 'success' : 'pending');
                addLog(data.message, data.committed ? 'success' : 'info');
                break;
                
            case 'cicd':
                updateBadge('cicd-status', data.status);
                document.getElementById('build-status').textContent = data.build || '-';
                addLog(data.message, data.status === 'success' ? 'success' : 'info');
                break;
                
            case 'comparison':
                document.getElementById('comparison-section').style.display = 'block';
                
                document.getElementById('before-effort').textContent = data.before.manual_effort;
                document.getElementById('before-tests').textContent = data.before.test_cases;
                document.getElementById('before-coverage').textContent = data.before.coverage;
                
                document.getElementById('after-time').textContent = data.after.ai_time;
                document.getElementById('after-tests').textContent = data.after.test_cases;
                document.getElementById('after-lines').textContent = data.after.lines_of_code;
                
                addLog('Comparison: Manual vs AI automation', 'success');
                break;
                
            case 'error':
                addLog(`Error: ${data.message}`, 'error');
                break;
        }
    };

    eventSource.onerror = function(error) {
        console.error('SSE Error:', error);
        updateStatusIndicator('Connection lost - Reconnecting...');
        addLog('Connection lost. Attempting to reconnect...', 'error');
        
        if (eventSource) {
            eventSource.close();
        }
        
        reconnectAttempts++;
        if (reconnectAttempts <= MAX_RECONNECT_ATTEMPTS) {
            const delay = Math.min(1000 * reconnectAttempts, 5000);
            console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
            setTimeout(() => {
                addLog(`Reconnecting... (attempt ${reconnectAttempts})`, 'info');
                connectSSE();
            }, delay);
        } else {
            addLog('Max reconnection attempts reached. Please refresh the page.', 'error');
            updateStatusIndicator('Disconnected');
        }
    };
}

// Initialize connection
connectSSE();

// Handle page visibility
document.addEventListener('visibilitychange', function() {
    if (!document.hidden && eventSource && eventSource.readyState === EventSource.CLOSED) {
        addLog('Page visible - reconnecting...', 'info');
        reconnectAttempts = 0;
        connectSSE();
    }
});

// Initialize
updateTimestamp();
setInterval(updateTimestamp, 1000);
addLog('Dashboard initialized', 'info');

// Hide buttons initially
document.getElementById('coverage-btn').style.display = 'none';
document.getElementById('tests-btn').style.display = 'none';