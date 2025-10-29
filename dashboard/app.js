// SSE Connection with auto-reconnect
let eventSource = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
let allLogs = [];

// Feature state management
const featureState = {
    healings: [],
    errors: [],
    diffs: [],
    anomalies: []
};

// Tab Management
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            button.classList.add('active');
            const targetPane = document.getElementById(`${tabName}-tab`);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        });
    });
}

// Initialize tabs when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
    
    // Hide buttons initially
    document.getElementById('coverage-btn').style.display = 'none';
    document.getElementById('tests-btn').style.display = 'none';
    document.getElementById('test-results-section').style.display = 'none';
    
    addLog('Dashboard initialized successfully', 'success');
    addLog('Waiting for automation tasks...', 'info');
    
    // IMPORTANT: Start SSE connection immediately
    connectSSE();
});

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
    console.log('🔌 Attempting to connect SSE...');
    
    if (eventSource) {
        console.log('Closing existing SSE connection');
        eventSource.close();
    }
    
    eventSource = new EventSource('/events');
    console.log('✓ SSE EventSource created');
    
    eventSource.onopen = function() {
        reconnectAttempts = 0;
        console.log('✅ SSE connection opened successfully');
        updateStatus('Connected - Ready');
        addLog('Connected to automation server', 'success');
    };

    eventSource.onmessage = function(event) {
        console.log('📨 SSE message received:', event.data);
        const data = JSON.parse(event.data);
        console.log('📦 Parsed data:', data);
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
                console.log('🧪 Execute event received:', data);
                document.getElementById('tests-passed').textContent = data.passed || 0;
                document.getElementById('tests-failed').textContent = data.failed || 0;
                document.getElementById('tests-total').textContent = data.total || 0;
                
                const statusText = `Test execution complete: ${data.passed || 0}/${data.total || 0} passed`;
                addLog(statusText, data.failed === 0 ? 'success' : 'warning');
                
                // Show and populate test results
                if (data.details && data.details.length > 0) {
                    console.log(`📋 Populating ${data.details.length} test details`);
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
                    console.log('✅ Test details populated');
                } else {
                    console.warn('⚠️ No test details found in execute event');
                }
                break;
                
            case 'coverage':
                const percentage = data.percentage || 0;
                const linesCovered = data.lines_covered || 0;
                const linesTotal = data.lines_total || 0;
                const linesMissing = linesTotal - linesCovered;
                
                updateCoverage(percentage);
                
                // Update coverage details
                document.getElementById('coverage-lines-covered').textContent = linesCovered;
                document.getElementById('coverage-lines-total').textContent = linesTotal;
                document.getElementById('coverage-lines-missing').textContent = linesMissing;
                
                addLog(`Code coverage analysis: ${percentage}% (${linesCovered}/${linesTotal} lines, ${linesMissing} missing)`, 
                       percentage >= 80 ? 'success' : percentage >= 70 ? 'warning' : 'error');
                
                if (percentage > 0) {
                    document.getElementById('coverage-btn').style.display = 'inline-flex';
                }
                break;
                
            case 'contract':
                console.log('📜 Contract event received:', data);
                document.getElementById('contracts-tested').textContent = data.total || 0;
                document.getElementById('contracts-passed').textContent = data.passed || 0;
                document.getElementById('contracts-failed').textContent = data.failed || 0;
                
                if (data.status === 'completed') {
                    console.log('✅ Contract testing completed');
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
            
            // New feature events
            case 'healing':
                handleHealingEvent(data);
                break;
            
            case 'healing_summary':
                handleHealingSummaryEvent(data);
                break;
            
            case 'error_analysis':
                handleErrorAnalysisEvent(data);
                break;
            
            case 'api_diff':
                handleAPIDiffEvent(data);
                break;
            
            case 'test_regeneration':
                handleTestRegenerationEvent(data);
                break;
            
            case 'anomaly':
                handleAnomalyEvent(data);
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

// DON'T call connectSSE() here - it's called in DOMContentLoaded
// connectSSE();

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

// ===============================================
// NEW FEATURE EVENT HANDLERS
// ===============================================

/**
 * Handle self-healing event
 * Updates healing list and statistics
 */
function handleHealingEvent(data) {
    featureState.healings.push(data);
    
    // Update badge
    const badge = document.getElementById('healing-badge');
    if (badge) badge.textContent = featureState.healings.length;
    
    // Add to healing list
    const healingList = document.getElementById('healing-list');
    if (healingList) {
        // Remove empty state
        const emptyState = healingList.querySelector('.empty-state');
        if (emptyState) emptyState.remove();
        
        const healingItem = createHealingItem(data);
        healingList.insertBefore(healingItem, healingList.firstChild);
    }
    
    // Update stats
    updateHealingStats();
    
    addLog(`Self-Healing: Fixed ${data.test_name} (${Math.round(data.confidence * 100)}% confidence)`, 'success');
}

/**
 * Create healing item element
 */
function createHealingItem(data) {
    const item = document.createElement('div');
    item.className = 'healing-item';
    
    const confidence = Math.round((data.confidence || 0) * 100);
    const status = confidence >= 80 ? 'Applied' : 'Needs Review';
    const statusClass = confidence >= 80 ? '' : 'review';
    
    item.innerHTML = `
        <div class="healing-item-header">
            <span class="healing-test-name">${data.test_name || 'Unknown Test'}</span>
            <div class="healing-confidence">
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidence}%"></div>
                </div>
                <span>${confidence}%</span>
            </div>
        </div>
        <div class="healing-meta">
            <span>⏱ ${formatTimestamp(data.timestamp || Date.now())}</span>
            <span class="healing-status ${statusClass}">${status}</span>
        </div>
    `;
    
    // Click to show diff
    item.addEventListener('click', () => {
        showCodeDiff(data.diff || { before: data.old_code, after: data.new_code });
    });
    
    return item;
}

/**
 * Update healing statistics
 */
function updateHealingStats() {
    const total = featureState.healings.length;
    const successful = featureState.healings.filter(h => (h.confidence || 0) >= 0.8).length;
    const successRate = total > 0 ? Math.round((successful / total) * 100) : 0;
    const avgConfidence = total > 0
        ? Math.round(featureState.healings.reduce((sum, h) => sum + (h.confidence || 0), 0) / total * 100)
        : 0;
    
    const totalEl = document.getElementById('total-healings');
    const rateEl = document.getElementById('success-rate');
    const confEl = document.getElementById('avg-confidence');
    
    if (totalEl) totalEl.textContent = total;
    if (rateEl) rateEl.textContent = `${successRate}%`;
    if (confEl) confEl.textContent = `${avgConfidence}%`;
}

/**
 * Show code diff in the diff viewer
 */
function showCodeDiff(diff) {
    const diffViewer = document.getElementById('code-diff');
    if (!diffViewer) return;
    
    const beforeLines = (diff.before || '').split('\n');
    const afterLines = (diff.after || '').split('\n');
    
    let beforeHtml = '';
    let afterHtml = '';
    
    const maxLines = Math.max(beforeLines.length, afterLines.length);
    
    for (let i = 0; i < maxLines; i++) {
        const beforeLine = beforeLines[i] || '';
        const afterLine = afterLines[i] || '';
        
        if (beforeLine !== afterLine) {
            if (beforeLine) {
                beforeHtml += `<div class="diff-line removed">
                    <span class="diff-line-prefix">-</span>
                    <span class="diff-line-content">${escapeHtml(beforeLine)}</span>
                </div>`;
            }
            if (afterLine) {
                afterHtml += `<div class="diff-line added">
                    <span class="diff-line-prefix">+</span>
                    <span class="diff-line-content">${escapeHtml(afterLine)}</span>
                </div>`;
            }
        } else {
            beforeHtml += `<div class="diff-line">
                <span class="diff-line-prefix"> </span>
                <span class="diff-line-content">${escapeHtml(beforeLine)}</span>
            </div>`;
            afterHtml += `<div class="diff-line">
                <span class="diff-line-prefix"> </span>
                <span class="diff-line-content">${escapeHtml(afterLine)}</span>
            </div>`;
        }
    }
    
    diffViewer.innerHTML = `
        <div class="code-diff">
            <div class="diff-section">
                <div class="diff-header">Before (Original)</div>
                <div class="diff-content">${beforeHtml}</div>
            </div>
            <div class="diff-section">
                <div class="diff-header">After (Healed)</div>
                <div class="diff-content">${afterHtml}</div>
            </div>
        </div>
    `;
}

/**
 * Handle healing summary event (after test re-run)
 */
function handleHealingSummaryEvent(data) {
    const {
        healed_count,
        before_passed,
        before_failed,
        after_passed,
        after_failed,
        tests_fixed,
        effectiveness
    } = data;
    
    // Create summary banner
    const testResultsSection = document.querySelector('.test-results');
    if (testResultsSection) {
        // Remove existing summary banner if present
        const existingBanner = testResultsSection.querySelector('.healing-summary-banner');
        if (existingBanner) existingBanner.remove();
        
        const banner = document.createElement('div');
        banner.className = 'healing-summary-banner';
        banner.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        banner.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0 0 10px 0; font-size: 18px;">
                        🔧 Self-Healing Complete
                    </h3>
                    <p style="margin: 0; opacity: 0.9;">
                        Healed ${healed_count} test(s), ${tests_fixed} now passing
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 32px; font-weight: bold; margin-bottom: 5px;">
                        ${Math.round(effectiveness)}%
                    </div>
                    <div style="opacity: 0.9; font-size: 12px;">Effectiveness</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2);">
                <div>
                    <div style="opacity: 0.8; font-size: 12px;">Before Healing</div>
                    <div style="font-size: 16px; margin-top: 5px;">
                        ✓ ${before_passed} passed · ✗ ${before_failed} failed
                    </div>
                </div>
                <div>
                    <div style="opacity: 0.8; font-size: 12px;">After Healing</div>
                    <div style="font-size: 16px; margin-top: 5px;">
                        ✓ ${after_passed} passed · ✗ ${after_failed} failed
                    </div>
                </div>
            </div>
        `;
        
        testResultsSection.insertBefore(banner, testResultsSection.firstChild);
    }
    
    // Update healing stats
    updateHealingStats();
    
    // Log the summary
    addLog(
        `Healing Summary: ${tests_fixed}/${healed_count} tests fixed (${Math.round(effectiveness)}% effective)`,
        'success'
    );
}

/**
 * Handle error analysis event
 */
function handleErrorAnalysisEvent(data) {
    featureState.errors.push(data);
    
    // Update badge
    const badge = document.getElementById('error-badge');
    if (badge) badge.textContent = featureState.errors.length;
    
    // Add to error list
    const errorList = document.getElementById('error-list');
    if (errorList) {
        const emptyState = errorList.querySelector('.empty-state');
        if (emptyState) emptyState.remove();
        
        const errorItem = createErrorItem(data);
        errorList.insertBefore(errorItem, errorList.firstChild);
    }
    
    // Update stats
    updateErrorStats();
    
    addLog(`Error Analysis: ${data.test_name} - ${data.error_type}`, 'error');
}

/**
 * Create error item element
 */
function createErrorItem(data) {
    const item = document.createElement('div');
    item.className = 'error-item';
    
    item.innerHTML = `
        <div class="error-item-header">
            <div class="error-icon">✕</div>
            <div class="error-content">
                <div class="error-title">${data.test_name || 'Unknown Test'}</div>
                <div class="error-message">${data.error_type || 'Error'}: ${truncate(data.message || '', 80)}</div>
            </div>
        </div>
        <div class="error-meta">
            <span>⏱ ${formatTimestamp(data.timestamp || Date.now())}</span>
            <span>📊 ${data.root_cause || 'Analyzing...'}</span>
        </div>
    `;
    
    // Click to show details
    item.addEventListener('click', () => {
        showErrorDetails(data);
    });
    
    return item;
}

/**
 * Update error statistics
 */
function updateErrorStats() {
    const total = featureState.errors.length;
    const uniqueTypes = new Set(featureState.errors.map(e => e.error_type)).size;
    
    const totalEl = document.getElementById('total-errors');
    const typesEl = document.getElementById('unique-types');
    
    if (totalEl) totalEl.textContent = total;
    if (typesEl) typesEl.textContent = uniqueTypes;
}

/**
 * Show detailed error information
 */
function showErrorDetails(error) {
    const detailsDiv = document.getElementById('error-details');
    if (!detailsDiv) return;
    
    let html = `
        <div class="error-details">
            <div class="error-section">
                <div class="error-section-title">Error Details</div>
                <div class="error-section-content">
                    <strong>Type:</strong> ${error.error_type || 'Unknown'}<br>
                    <strong>Test:</strong> ${error.test_name || 'Unknown'}<br>
                    <strong>Root Cause:</strong> ${error.root_cause || 'Analyzing...'}<br>
                    <strong>Message:</strong> ${error.message || 'No message'}
                </div>
            </div>
    `;
    
    if (error.request) {
        html += `
            <div class="error-section">
                <div class="error-section-title">Request</div>
                <div class="error-section-content">
                    <strong>${error.request.method || 'GET'}</strong> ${error.request.url || ''}<br>
                    ${error.request.headers ? `<strong>Headers:</strong> ${JSON.stringify(error.request.headers, null, 2)}` : ''}
                </div>
            </div>
        `;
    }
    
    if (error.response) {
        html += `
            <div class="error-section">
                <div class="error-section-title">Response</div>
                <div class="error-section-content">
                    <strong>Status:</strong> ${error.response.status_code || 'N/A'}<br>
                    ${error.response.body ? `<strong>Body:</strong> ${JSON.stringify(error.response.body, null, 2)}` : ''}
                </div>
            </div>
        `;
    }
    
    if (error.suggestions && error.suggestions.length > 0) {
        html += `
            <div class="error-section">
                <div class="error-section-title">Fix Suggestions</div>
                <ul class="fix-suggestions">
                    ${error.suggestions.map(s => `<li class="fix-suggestion">${s}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    html += '</div>';
    detailsDiv.innerHTML = html;
}

/**
 * Handle API diff event
 */
function handleAPIDiffEvent(data) {
    if (data.changes && Array.isArray(data.changes)) {
        featureState.diffs.push(...data.changes);
    }
    
    // Update badges
    const breaking = featureState.diffs.filter(d => d.breaking).length;
    const nonBreaking = featureState.diffs.length - breaking;
    
    const breakingEl = document.getElementById('breaking-count');
    const nonBreakingEl = document.getElementById('non-breaking-count');
    const totalEl = document.getElementById('total-changes');
    
    if (breakingEl) breakingEl.textContent = breaking;
    if (nonBreakingEl) nonBreakingEl.textContent = nonBreaking;
    if (totalEl) totalEl.textContent = featureState.diffs.length;
    
    // Update diff badge
    const badge = document.getElementById('diff-badge');
    if (badge) badge.textContent = featureState.diffs.length;
    
    // Update diff list
    const changeList = document.getElementById('change-list');
    if (changeList) {
        const emptyState = changeList.querySelector('.empty-state');
        if (emptyState) emptyState.remove();
        
        featureState.diffs.forEach(change => {
            const changeItem = createChangeItem(change);
            changeList.appendChild(changeItem);
        });
    }
    
    addLog(`API Diff: ${data.changes ? data.changes.length : 0} changes detected`, 'info');
}

/**
 * Create change item element
 */
function createChangeItem(change) {
    const item = document.createElement('div');
    item.className = `change-item ${change.breaking ? 'breaking' : 'non-breaking'}`;
    
    const typeClass = (change.type || 'modified').toLowerCase();
    
    item.innerHTML = `
        <span class="change-type ${typeClass}">${change.type || 'Modified'}</span>
        <div class="change-path">${change.path || 'Unknown path'}</div>
        <div class="change-description">${change.description || 'No description'}</div>
        ${change.recommendation ? `
            <div class="change-recommendation">
                <strong>Recommendation:</strong> ${change.recommendation}
            </div>
        ` : ''}
    `;
    
    return item;
}

/**
 * Handle test regeneration event
 */
function handleTestRegenerationEvent(data) {
    console.log('🔄 TEST REGENERATION EVENT RECEIVED:', data);
    
    const {
        preserved_count,
        regenerated_count,
        total_count,
        changed_endpoints,
        unchanged_endpoints,
        spec_changes
    } = data;
    
    console.log('📊 Extracted values:', {
        preserved_count,
        regenerated_count,
        total_count,
        changed_endpoints,
        unchanged_endpoints
    });
    
    // Create regeneration banner in the Test Regeneration tab
    const healingList = document.getElementById('healing-list');
    console.log('🎯 healing-list element:', healingList);
    
    if (healingList) {
        // Remove empty state
        const emptyState = healingList.querySelector('.empty-state');
        if (emptyState) emptyState.remove();
        
        // Remove existing banner if present
        const existingBanner = healingList.querySelector('.regeneration-banner');
        if (existingBanner) existingBanner.remove();
        
        const banner = document.createElement('div');
        banner.className = 'regeneration-banner';
        banner.style.cssText = `
            background: white;
            color: black;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #e5e7eb;
        `;
        
        const effectiveness = preserved_count > 0 ? 
            Math.round((preserved_count / total_count) * 100) : 0;
        
        banner.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0 0 10px 0; font-size: 18px; color: black;">
                        Selective Test Regeneration
                    </h3>
                    <p style="margin: 0; color: #666;">
                        Smart regeneration: ${preserved_count} tests preserved, ${regenerated_count} regenerated
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 32px; font-weight: bold; margin-bottom: 5px; color: black;">
                        ${effectiveness}%
                    </div>
                    <div style="color: #666; font-size: 12px;">Tests Preserved</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                <div>
                    <div style="color: #666; font-size: 12px;">Preserved Tests</div>
                    <div style="font-size: 16px; margin-top: 5px; color: black;">
                        ${preserved_count} tests (${unchanged_endpoints ? unchanged_endpoints.length : 0} endpoints)
                    </div>
                </div>
                <div>
                    <div style="color: #666; font-size: 12px;">Regenerated Tests</div>
                    <div style="font-size: 16px; margin-top: 5px; color: black;">
                        ${regenerated_count} tests (${changed_endpoints ? changed_endpoints.length : 0} endpoints)
                    </div>
                </div>
            </div>
            ${changed_endpoints && changed_endpoints.length > 0 ? `
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                    <div style="color: #666; font-size: 12px; margin-bottom: 8px;">Changed Endpoints:</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        ${changed_endpoints.map(ep => `
                            <span style="background: #f3f4f6; color: black; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                                ${ep}
                            </span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
        
        healingList.insertBefore(banner, healingList.firstChild);
    }
    
    // Update stats in Test Regeneration tab (outside the if block to ensure it runs)
    const totalHealings = document.getElementById('total-healings');
    const successRate = document.getElementById('success-rate');
    const avgConfidence = document.getElementById('avg-confidence');
    
    console.log('🎯 DOM Elements found:', {
        totalHealings: totalHealings,
        successRate: successRate,
        avgConfidence: avgConfidence
    });
    
    console.log('📈 Updating Test Regeneration stats:', {
        total_count: total_count,
        preserved_count: preserved_count,
        regenerated_count: regenerated_count,
        preservedPercent: preserved_count > 0 ? Math.round((preserved_count / total_count) * 100) : 0
    });
    
    // Total Healings = Total test count (shows all tests including preserved + regenerated)
    if (totalHealings) {
        totalHealings.textContent = total_count || 0;
        console.log('✅ Set totalHealings to:', total_count);
    } else {
        console.error('❌ totalHealings element not found!');
    }
    
    // Success Rate = Percentage of tests preserved (not regenerated)
    const preservedPercent = preserved_count > 0 ? Math.round((preserved_count / total_count) * 100) : 0;
    if (successRate) {
        successRate.textContent = preservedPercent + '%';
        console.log('✅ Set successRate to:', preservedPercent + '%');
    } else {
        console.error('❌ successRate element not found!');
    }
    
    // Average Confidence = Number of tests regenerated
    if (avgConfidence) {
        avgConfidence.textContent = regenerated_count;
        console.log('✅ Set avgConfidence to:', regenerated_count);
    } else {
        console.error('❌ avgConfidence element not found!');
    }
    
    // Update the tab badge with total count
    const healingBadge = document.getElementById('healing-badge');
    if (healingBadge) {
        healingBadge.textContent = total_count || 0;
        console.log('✅ Set healing-badge to:', total_count);
    } else {
        console.error('❌ healing-badge element not found!');
    }
    
    // Update Overview tab to show selective regeneration breakdown
    const testsLabel = document.getElementById('tests-label');
    const testsGenerated = document.getElementById('tests-generated');
    const selectiveBreakdown = document.getElementById('selective-breakdown');
    const preservedCountEl = document.getElementById('preserved-count');
    const regeneratedCountEl = document.getElementById('regenerated-count');
    
    if (testsLabel && testsGenerated && selectiveBreakdown) {
        testsLabel.textContent = 'Total Tests';
        testsGenerated.textContent = total_count;
        selectiveBreakdown.style.display = 'block';
        preservedCountEl.textContent = `${preserved_count} preserved`;
        regeneratedCountEl.textContent = `${regenerated_count} regenerated`;
    }
    
    // Display spec changes in "Spec Changes & Test Impact" section
    if (spec_changes && spec_changes.length > 0) {
        const codeDiff = document.getElementById('code-diff');
        if (codeDiff) {
            // Remove empty state
            const emptyState = codeDiff.querySelector('.empty-state');
            if (emptyState) emptyState.remove();
            
            // Clear previous content
            codeDiff.innerHTML = '';
            
            // Display each change
            spec_changes.forEach((change, index) => {
                const changeDiv = document.createElement('div');
                changeDiv.style.cssText = `
                    background: #f8f9fa;
                    border-left: 4px solid ${change.breaking ? '#dc3545' : '#28a745'};
                    padding: 15px;
                    margin-bottom: 12px;
                    border-radius: 4px;
                `;
                
                const changeType = change.type.replace(/_/g, ' ').toUpperCase();
                const breakingBadge = change.breaking ? 
                    '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px; margin-left: 8px;">BREAKING</span>' : '';
                
                changeDiv.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div>
                            <strong style="color: #333;">${changeType}</strong>
                            ${breakingBadge}
                        </div>
                        <code style="background: #e9ecef; padding: 2px 8px; border-radius: 3px; font-size: 12px;">
                            ${change.method || ''} ${change.path || ''}
                        </code>
                    </div>
                    <div style="color: #666; font-size: 14px; margin-bottom: 8px;">
                        ${change.description}
                    </div>
                    ${change.recommendation ? `
                        <div style="background: #fff3cd; padding: 10px; border-radius: 4px; font-size: 13px; margin-top: 8px;">
                            <strong>💡 Recommendation:</strong> ${change.recommendation}
                        </div>
                    ` : ''}
                `;
                
                codeDiff.appendChild(changeDiv);
            });
        }
    }
    
    // Log the regeneration
    addLog(
        `Test Regeneration: ${preserved_count} preserved + ${regenerated_count} regenerated = ${total_count} total`,
        'success'
    );
}

/**
 * Handle anomaly event
 */
function handleAnomalyEvent(data) {
    featureState.anomalies.push(data);
    
    // Update badge
    const badge = document.getElementById('anomaly-badge');
    if (badge) badge.textContent = featureState.anomalies.length;
    
    // Add to anomaly list
    const anomalyList = document.getElementById('anomaly-list');
    if (anomalyList) {
        const emptyState = anomalyList.querySelector('.empty-state');
        if (emptyState) emptyState.remove();
        
        const anomalyItem = createAnomalyItem(data);
        anomalyList.insertBefore(anomalyItem, anomalyList.firstChild);
    }
    
    addLog(`Anomaly Detected: ${data.severity || 'Unknown'} - ${data.type || 'Unknown type'}`, 'warning');
}

/**
 * Create anomaly item element
 */
function createAnomalyItem(data) {
    const item = document.createElement('div');
    item.className = `anomaly-item ${(data.severity || 'medium').toLowerCase()}`;
    
    item.innerHTML = `
        <div class="anomaly-header">
            <span class="anomaly-title">${data.endpoint || 'Unknown endpoint'}</span>
            <span class="anomaly-severity ${(data.severity || 'medium').toLowerCase()}">${data.severity || 'Medium'}</span>
        </div>
        <div class="anomaly-description">${data.description || 'Anomaly detected'}</div>
        <div class="anomaly-values">
            <div class="anomaly-value">
                <span class="anomaly-value-label">Expected:</span>
                <span class="anomaly-value-number">${data.expected || 'N/A'}</span>
            </div>
            <div class="anomaly-value">
                <span class="anomaly-value-label">Actual:</span>
                <span class="anomaly-value-number">${data.actual || 'N/A'}</span>
            </div>
        </div>
        <div class="anomaly-meta" style="margin-top: 8px; font-size: 11px; color: var(--gray-600);">
            <span>⏱ ${formatTimestamp(data.timestamp || Date.now())}</span>
        </div>
    `;
    
    return item;
}

/**
 * Format timestamp to relative time
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return date.toLocaleDateString();
}

/**
 * Truncate string to specified length
 */
function truncate(str, length) {
    if (!str || str.length <= length) return str;
    return str.substring(0, length) + '...';
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return (text || '').replace(/[&<>"']/g, m => map[m]);
}
