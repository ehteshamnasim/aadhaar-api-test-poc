// SSE Connection with auto-reconnect
let eventSource = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
let allLogs = [];

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
    
    const timestamp = new Date().toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const logText = `[${timestamp}] ${message}`;
    entry.textContent = logText;
    allLogs.push({ time: timestamp, message, type });
    
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Clear logs
function clearLogs() {
    document.getElementById('log').innerHTML = '';
    allLogs = [];
    addLog('Log cleared', 'info');
}

// Export logs
function exportLogs() {
    if (allLogs.length === 0) {
        alert('No logs to export');
        return;
    }
    
    const logContent = allLogs.map(log => 
        `[${log.time}] [${log.type.toUpperCase()}] ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `api-test-logs-${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Close test results
function closeTestResults() {
    document.getElementById('test-results-section').style.display = 'none';
}

// Update coverage
function updateCoverage(percentage) {
    const circle = document.getElementById('coverage-circle');
    const text = document.getElementById('coverage-text');
    const circumference = 251.2; // 2 * π * 40
    const offset = circumference - (percentage / 100) * circumference;
    
    circle.style.strokeDashoffset = offset;
    text.textContent = `${percentage}%`;
    
    if (percentage >= 85) {
        circle.style.stroke = '#22c55e';
    } else if (percentage >= 70) {
        circle.style.stroke = '#f59e0b';
    } else {
        circle.style.stroke = '#f44d30';
    }
}

// Update badge
function updateBadge(elementId, status) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.className = element.classList[0]; // Keep first class
    
    switch(status) {
        case 'success':
        case 'passed':
        case 'completed':
            element.classList.add('success');
            element.textContent = '✓ Passed';
            break;
        case 'failed':
        case 'error':
            element.classList.add('error');
            element.textContent = '✗ Failed';
            break;
        case 'running':
        case 'in_progress':
            element.classList.add('running');
            element.textContent = '● Running';
            break;
        case 'warning':
        case 'triggered':
            element.classList.add('warning');
            element.textContent = '→ Triggered';
            break;
        default:
            element.textContent = status || 'Pending';
    }
}

// Update status
function updateStatus(status) {
    const statusElement = document.getElementById('status');
    const statusIcon = document.querySelector('.stat-icon');
    
    statusElement.textContent = status;
    
    if (status.includes('Connected') || status.includes('Ready')) {
        statusIcon.style.color = '#22c55e';
    } else if (status.includes('Error') || status.includes('Failed')) {
        statusIcon.style.color = '#ef4444';
    } else if (status.includes('Running') || status.includes('Processing')) {
        statusIcon.style.color = '#f59e0b';
    } else {
        statusIcon.style.color = '#6b7280';
    }
}

// Reset dashboard
function resetDashboard() {
    if (!confirm('Are you sure you want to reset the dashboard? This will clear all current data.')) {
        return;
    }
    
    // Reset values
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
    
    // Reset badges
    updateBadge('parse-status', 'Pending');
    updateBadge('gen-status', 'Pending');
    updateBadge('syntax-check', '-');
    updateBadge('import-check', '-');
    updateBadge('validation-status', 'Pending');
    updateBadge('git-commit', 'Pending');
    updateBadge('git-push', 'Pending');
    updateBadge('cicd-status', 'Not Started');
    
    // Reset progress
    document.getElementById('gen-progress').style.width = '0%';
    document.getElementById('gen-percentage').textContent = '0%';
    updateCoverage(0);
    
    // Hide sections
    document.getElementById('comparison-section').style.display = 'none';
    document.getElementById('test-results-section').style.display = 'none';
    document.getElementById('coverage-btn').style.display = 'none';
    document.getElementById('tests-btn').style.display = 'none';
    
    // Clear logs
    clearLogs();
    
    updateStatus('Dashboard Reset');
    addLog('Dashboard reset - ready for new test run', 'info');
}

// Handle SSE events
function connectSSE() {
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource('/events');
    
    eventSource.onopen = function() {
        reconnectAttempts = 0;
        updateStatus('Connected - Ready');
        addLog('Connected to automation server', 'success');
    };

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateTimestamp();
        
        switch(data.type) {
            case 'connected':
                addLog('Dashboard connected successfully', 'info');
                break;
                
            case 'clear':
                // Reset all metric values
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
                
                // Reset badges
                updateBadge('parse-status', 'Pending');
                updateBadge('gen-status', 'Pending');
                updateBadge('syntax-check', '-');
                updateBadge('import-check', '-');
                updateBadge('validation-status', 'Pending');
                updateBadge('git-commit', 'Pending');
                updateBadge('git-push', 'Pending');
                updateBadge('cicd-status', 'Not Started');
                
                // Reset progress
                document.getElementById('gen-progress').style.width = '0%';
                document.getElementById('gen-percentage').textContent = '0%';
                updateCoverage(0);
                
                // Hide sections
                document.getElementById('comparison-section').style.display = 'none';
                document.getElementById('test-results-section').style.display = 'none';
                document.getElementById('coverage-btn').style.display = 'none';
                document.getElementById('tests-btn').style.display = 'none';
                
                // Clear test results list
                const testDetailsList = document.getElementById('test-details-list');
                if (testDetailsList) {
                    testDetailsList.innerHTML = '';
                }
                
                addLog('Starting new automation run...', 'info');
                break;
                
            case 'status':
                updateStatus(data.message);
                addLog(data.message, 'info');
                break;
                
            case 'parse':
                document.getElementById('spec-file').textContent = data.file || 'specs/api.yaml';
                document.getElementById('endpoint-count').textContent = data.endpoints || 0;
                updateBadge('parse-status', 'success');
                addLog(`API specification parsed: ${data.endpoints || 0} endpoints discovered`, 'success');
                break;
            
            case 'test_created':
                document.getElementById('tests-generated').textContent = data.test_number;
                addLog(`Generated test ${data.test_number}: ${data.test_name}`, 'info');
                break;
                
            case 'generate':
                const progress = data.progress || 0;
                document.getElementById('gen-progress').style.width = progress + '%';
                document.getElementById('gen-percentage').textContent = progress + '%';
                
                if (data.count > 0) {
                    document.getElementById('tests-generated').textContent = data.count;
                }
                
                updateBadge('gen-status', data.status || 'running');
                
                if (data.message) {
                    addLog(data.message, data.status === 'success' ? 'success' : 'info');
                }
                
                if (data.status === 'success' && data.count > 0) {
                    document.getElementById('tests-btn').style.display = 'inline-flex';
                    addLog(`Test generation complete: ${data.count} tests created`, 'success');
                }
                break;
                
            case 'validate':
                updateBadge('syntax-check', data.syntax ? '✓' : '✗');
                updateBadge('import-check', data.imports ? '✓' : '✗');
                updateBadge('validation-status', data.overall ? 'success' : 'failed');
                
                document.getElementById('syntax-check').style.color = data.syntax ? '#22c55e' : '#ef4444';
                document.getElementById('import-check').style.color = data.imports ? '#22c55e' : '#ef4444';
                
                addLog(data.message, data.overall ? 'success' : 'error');
                break;
                
            case 'execute':
                document.getElementById('tests-passed').textContent = data.passed || 0;
                document.getElementById('tests-failed').textContent = data.failed || 0;
                document.getElementById('tests-total').textContent = data.total || 0;
                
                const statusText = `Test execution complete: ${data.passed || 0}/${data.total || 0} passed`;
                addLog(statusText, data.failed === 0 ? 'success' : 'warning');
                
                // Show and populate test results
                if (data.details && data.details.length > 0) {
                    document.getElementById('test-results-section').style.display = 'block';
                    const detailsList = document.getElementById('test-details-list');
                    detailsList.innerHTML = '';
                    
                    data.details.forEach((detail) => {
                        const testDiv = document.createElement('div');
                        testDiv.className = `test-item ${detail.passed ? 'passed' : 'failed'}`;
                        testDiv.innerHTML = `
                            <span class="test-name">${detail.name}</span>
                            <div class="test-reason">${detail.reason}</div>
                        `;
                        detailsList.appendChild(testDiv);
                    });
                }
                break;
                
            case 'coverage':
                const percentage = data.percentage || 0;
                updateCoverage(percentage);
                addLog(`Code coverage analysis: ${percentage}%`, percentage >= 85 ? 'success' : 'warning');
                
                if (percentage > 0) {
                    document.getElementById('coverage-btn').style.display = 'inline-flex';
                }
                break;
                
            case 'contract':
                document.getElementById('contracts-tested').textContent = data.total || 0;
                document.getElementById('contracts-passed').textContent = data.passed || 0;
                document.getElementById('contracts-failed').textContent = data.failed || 0;
                
                if (data.status === 'completed') {
                    addLog(`Contract testing complete: ${data.passed}/${data.total} passed`, 
                           data.failed === 0 ? 'success' : 'warning');
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
                
                addLog('Performance comparison data generated', 'success');
                break;
                
            case 'error':
                addLog(`Error: ${data.message}`, 'error');
                break;
        }
    };

    eventSource.onerror = function(error) {
        console.error('SSE Error:', error);
        updateStatus('Connection Lost');
        addLog('Connection lost. Attempting to reconnect...', 'error');
        
        if (eventSource) {
            eventSource.close();
        }
        
       reconnectAttempts++;
        if (reconnectAttempts <= MAX_RECONNECT_ATTEMPTS) {
            const delay = Math.min(1000 * reconnectAttempts, 5000);
            setTimeout(() => {
                addLog(`Reconnecting... (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`, 'warning');
                connectSSE();
            }, delay);
        } else {
            addLog('Maximum reconnection attempts reached. Please refresh the page.', 'error');
            updateStatus('Disconnected');
        }
    };
}

// Initialize connection
connectSSE();

// Handle page visibility
document.addEventListener('visibilitychange', function() {
    if (!document.hidden && eventSource && eventSource.readyState === EventSource.CLOSED) {
        addLog('Page active - reconnecting to server...', 'info');
        reconnectAttempts = 0;
        connectSSE();
    }
});

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
    
    // Hide buttons initially
    document.getElementById('coverage-btn').style.display = 'none';
    document.getElementById('tests-btn').style.display = 'none';
    document.getElementById('test-results-section').style.display = 'none';
    
    addLog('Dashboard initialized successfully', 'success');
    addLog('Waiting for automation tasks...', 'info');
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to clear logs
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            clearLogs();
        }
        // Ctrl/Cmd + E to export logs
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            exportLogs();
        }
        // Escape to close test results
        if (e.key === 'Escape') {
            const testResults = document.getElementById('test-results-section');
            if (testResults.style.display !== 'none') {
                closeTestResults();
            }
        }
    });
    
    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});

// Error handling for network issues
window.addEventListener('online', function() {
    updateStatus('Network Restored');
    addLog('Network connection restored', 'success');
    if (eventSource && eventSource.readyState === EventSource.CLOSED) {
        reconnectAttempts = 0;
        connectSSE();
    }
});

window.addEventListener('offline', function() {
    updateStatus('Network Offline');
    addLog('Network connection lost', 'error');
});

// Performance monitoring
let performanceStartTime = null;

function startPerformanceTimer() {
    performanceStartTime = Date.now();
    addLog('Performance monitoring started', 'info');
}

function stopPerformanceTimer(taskName) {
    if (performanceStartTime) {
        const duration = ((Date.now() - performanceStartTime) / 1000).toFixed(2);
        addLog(`${taskName} completed in ${duration} seconds`, 'success');
        performanceStartTime = null;
    }
}

// Enhanced SSE message handler with performance tracking
const originalOnMessage = eventSource ? eventSource.onmessage : null;
if (eventSource) {
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        // Track performance for key operations
        if (data.type === 'parse' && data.status === 'starting') {
            startPerformanceTimer();
        } else if (data.type === 'parse' && data.status === 'success') {
            stopPerformanceTimer('API parsing');
        } else if (data.type === 'generate' && data.status === 'starting') {
            startPerformanceTimer();
        } else if (data.type === 'generate' && data.status === 'success') {
            stopPerformanceTimer('Test generation');
        } else if (data.type === 'execute' && data.status === 'starting') {
            startPerformanceTimer();
        } else if (data.type === 'execute' && data.status === 'completed') {
            stopPerformanceTimer('Test execution');
        }
        
        // Call original handler
        if (originalOnMessage) {
            originalOnMessage.call(this, event);
        }
    };
}

// Auto-refresh functionality (optional)
let autoRefreshInterval = null;

function toggleAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        addLog('Auto-refresh disabled', 'info');
    } else {
        autoRefreshInterval = setInterval(() => {
            if (eventSource && eventSource.readyState === EventSource.CLOSED) {
                addLog('Auto-refresh: Attempting reconnection', 'info');
                reconnectAttempts = 0;
                connectSSE();
            }
        }, 30000); // Check every 30 seconds
        addLog('Auto-refresh enabled (30s interval)', 'info');
    }
}

// Data export functionality
function exportDashboardData() {
    const dashboardData = {
        timestamp: new Date().toISOString(),
        apiSpec: {
            file: document.getElementById('spec-file').textContent,
            endpoints: document.getElementById('endpoint-count').textContent
        },
        testGeneration: {
            testsGenerated: document.getElementById('tests-generated').textContent,
            progress: document.getElementById('gen-percentage').textContent
        },
        testExecution: {
            passed: document.getElementById('tests-passed').textContent,
            failed: document.getElementById('tests-failed').textContent,
            total: document.getElementById('tests-total').textContent
        },
        coverage: document.getElementById('coverage-text').textContent,
        contractTesting: {
            tested: document.getElementById('contracts-tested').textContent,
            passed: document.getElementById('contracts-passed').textContent,
            failed: document.getElementById('contracts-failed').textContent
        },
        logs: allLogs
    };
    
    const blob = new Blob([JSON.stringify(dashboardData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard-data-${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    addLog('Dashboard data exported successfully', 'success');
}

// Add visual feedback for long-running operations
function showProcessingIndicator(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('loading');
    }
}

function hideProcessingIndicator(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('loading');
    }
}

// Enhanced error reporting
window.addEventListener('error', function(event) {
    console.error('Dashboard error:', event);
    addLog(`Dashboard error: ${event.message}`, 'error');
});

// Notification support (if browser supports)
function showNotification(title, message, type = 'info') {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(title, {
            body: message,
            icon: type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ',
            tag: 'api-test-automation',
            requireInteraction: false
        });
        
        setTimeout(() => notification.close(), 5000);
    }
}

// Request notification permission on load
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            addLog('Browser notifications enabled', 'success');
        }
    });
}

// Add tooltips for better UX
function initTooltips() {
    const elements = document.querySelectorAll('[data-tooltip]');
    elements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-popup';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltips = document.querySelectorAll('.tooltip-popup');
            tooltips.forEach(t => t.remove());
        });
    });
}

// Initialize tooltips when DOM is ready
document.addEventListener('DOMContentLoaded', initTooltips);

// Utility function to format numbers
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// Utility function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Add CSS for tooltip popup
const style = document.createElement('style');
style.textContent = `
    .tooltip-popup {
        position: fixed;
        background: var(--gray-900);
        color: var(--white);
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 10000;
        pointer-events: none;
        white-space: nowrap;
        animation: fadeIn 0.2s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);