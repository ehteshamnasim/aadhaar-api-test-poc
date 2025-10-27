/**
 * Enhanced Dashboard JavaScript
 * Handles tab navigation, SSE events, and real-time updates for all features
 */

// State management
const state = {
    healings: [],
    errors: [],
    diffs: [],
    anomalies: [],
    traffic: [],
    currentTab: 'overview'
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeSSE();
    setupEmptyStates();
});

/**
 * Initialize tab navigation
 * Sets up click handlers for tab buttons and manages active states
 */
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
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            state.currentTab = tabName;
        });
    });
}

/**
 * Initialize Server-Sent Events connection
 * Listens for events from the dashboard server and updates UI
 */
function initializeSSE() {
    const eventSource = new EventSource('/events');
    
    eventSource.addEventListener('spec_analysis', handleSpecAnalysis);
    eventSource.addEventListener('test_generation', handleTestGeneration);
    eventSource.addEventListener('test_execution', handleTestExecution);
    eventSource.addEventListener('healing', handleHealing);
    eventSource.addEventListener('error_analysis', handleErrorAnalysis);
    eventSource.addEventListener('api_diff', handleAPIDiff);
    eventSource.addEventListener('anomaly', handleAnomaly);
    eventSource.addEventListener('traffic', handleTraffic);
    eventSource.addEventListener('activity', handleActivity);
    
    eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        // Reconnection is automatic
    };
}

/**
 * Setup empty states for all lists
 * Shows placeholder messages when no data is available
 */
function setupEmptyStates() {
    const lists = [
        'healing-list',
        'error-list',
        'change-list',
        'anomaly-list',
        'traffic-list'
    ];
    
    lists.forEach(listId => {
        const list = document.getElementById(listId);
        if (list && list.children.length === 0) {
            showEmptyState(list, getEmptyMessage(listId));
        }
    });
}

/**
 * Get appropriate empty state message for a list
 * @param {string} listId - ID of the list element
 * @returns {string} Empty state message
 */
function getEmptyMessage(listId) {
    const messages = {
        'healing-list': 'No healing operations yet. Self-healing will appear here when tests are automatically repaired.',
        'error-list': 'No errors detected. All tests are passing!',
        'change-list': 'No API changes detected. Upload a new spec to compare.',
        'anomaly-list': 'No anomalies detected. System is operating normally.',
        'traffic-list': 'No traffic recorded. Start recording to capture API requests.'
    };
    return messages[listId] || 'No data available';
}

/**
 * Show empty state in a list
 * @param {HTMLElement} list - List element
 * @param {string} message - Message to display
 */
function showEmptyState(list, message) {
    list.innerHTML = `<div class="empty-state"><p>${message}</p></div>`;
}

/**
 * Handle spec analysis event
 * @param {Event} event - SSE event
 */
function handleSpecAnalysis(event) {
    const data = JSON.parse(event.data);
    addActivityLog('Spec Analysis', data.message || 'API specification analyzed');
}

/**
 * Handle test generation event
 * @param {Event} event - SSE event
 */
function handleTestGeneration(event) {
    const data = JSON.parse(event.data);
    addActivityLog('Test Generation', data.message || 'Tests generated');
}

/**
 * Handle test execution event
 * @param {Event} event - SSE event
 */
function handleTestExecution(event) {
    const data = JSON.parse(event.data);
    addActivityLog('Test Execution', data.message || 'Tests executed');
}

/**
 * Handle healing event
 * Updates healing list and badge counter
 * @param {Event} event - SSE event with healing data
 */
function handleHealing(event) {
    const data = JSON.parse(event.data);
    state.healings.push(data);
    
    // Update badge
    const badge = document.getElementById('healing-badge');
    if (badge) badge.textContent = state.healings.length;
    
    // Add to healing list
    const healingList = document.getElementById('healing-list');
    if (healingList.querySelector('.empty-state')) {
        healingList.innerHTML = '';
    }
    
    const healingItem = createHealingItem(data);
    healingList.insertBefore(healingItem, healingList.firstChild);
    
    // Update stats
    updateHealingStats();
    
    addActivityLog('Self-Healing', `Fixed: ${data.test_name}`);
}

/**
 * Create healing item element
 * @param {Object} data - Healing data
 * @returns {HTMLElement} Healing item element
 */
function createHealingItem(data) {
    const item = document.createElement('div');
    item.className = 'healing-item';
    
    const confidence = Math.round(data.confidence * 100);
    const status = confidence >= 80 ? 'success' : 'review';
    const statusText = confidence >= 80 ? 'Applied' : 'Needs Review';
    
    item.innerHTML = `
        <div class="healing-item-header">
            <span class="healing-test-name">${data.test_name}</span>
            <div class="healing-confidence">
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidence}%"></div>
                </div>
                <span>${confidence}%</span>
            </div>
        </div>
        <div class="healing-meta">
            <span>⏱ ${formatTimestamp(data.timestamp)}</span>
            <span class="healing-status ${status}">${statusText}</span>
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
 * Calculates total healings, success rate, and average confidence
 */
function updateHealingStats() {
    const total = state.healings.length;
    const successful = state.healings.filter(h => h.confidence >= 0.8).length;
    const successRate = total > 0 ? Math.round((successful / total) * 100) : 0;
    const avgConfidence = total > 0
        ? Math.round(state.healings.reduce((sum, h) => sum + h.confidence, 0) / total * 100)
        : 0;
    
    document.getElementById('total-healings').textContent = total;
    document.getElementById('success-rate').textContent = `${successRate}%`;
    document.getElementById('avg-confidence').textContent = `${avgConfidence}%`;
}

/**
 * Show code diff in the diff viewer
 * @param {Object} diff - Diff object with before/after code
 */
function showCodeDiff(diff) {
    const diffViewer = document.getElementById('code-diff');
    if (!diffViewer) return;
    
    const beforeLines = (diff.before || '').split('\n');
    const afterLines = (diff.after || '').split('\n');
    
    let beforeHtml = '';
    let afterHtml = '';
    
    // Simple line-by-line comparison
    const maxLines = Math.max(beforeLines.length, afterLines.length);
    
    for (let i = 0; i < maxLines; i++) {
        const beforeLine = beforeLines[i] || '';
        const afterLine = afterLines[i] || '';
        
        if (beforeLine && !afterLine) {
            beforeHtml += `<div class="diff-line removed">
                <span class="diff-line-prefix">-</span>
                <span class="diff-line-content">${escapeHtml(beforeLine)}</span>
            </div>`;
        } else if (!beforeLine && afterLine) {
            afterHtml += `<div class="diff-line added">
                <span class="diff-line-prefix">+</span>
                <span class="diff-line-content">${escapeHtml(afterLine)}</span>
            </div>`;
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
        <div class="diff-section">
            <div class="diff-header">Before (Original)</div>
            <div class="diff-content">${beforeHtml}</div>
        </div>
        <div class="diff-section">
            <div class="diff-header">After (Healed)</div>
            <div class="diff-content">${afterHtml}</div>
        </div>
    `;
}

/**
 * Handle error analysis event
 * Updates error list and badge counter
 * @param {Event} event - SSE event with error data
 */
function handleErrorAnalysis(event) {
    const data = JSON.parse(event.data);
    state.errors.push(data);
    
    // Update badge
    const badge = document.getElementById('error-badge');
    if (badge) badge.textContent = state.errors.length;
    
    // Add to error list
    const errorList = document.getElementById('error-list');
    if (errorList.querySelector('.empty-state')) {
        errorList.innerHTML = '';
    }
    
    const errorItem = createErrorItem(data);
    errorList.insertBefore(errorItem, errorList.firstChild);
    
    // Update stats
    updateErrorStats();
    
    addActivityLog('Error Analysis', `Analyzed: ${data.test_name}`);
}

/**
 * Create error item element
 * @param {Object} data - Error data
 * @returns {HTMLElement} Error item element
 */
function createErrorItem(data) {
    const item = document.createElement('div');
    item.className = 'error-item';
    
    item.innerHTML = `
        <div class="error-item-header">
            <div class="error-icon">✕</div>
            <div class="error-content">
                <div class="error-title">${data.test_name}</div>
                <div class="error-message">${data.error_type}: ${truncate(data.message, 80)}</div>
            </div>
        </div>
        <div class="error-meta">
            <span>⏱ ${formatTimestamp(data.timestamp)}</span>
            <span>📊 ${data.root_cause || 'Unknown cause'}</span>
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
 * Calculates total errors, unique types, and distribution
 */
function updateErrorStats() {
    const total = state.errors.length;
    const uniqueTypes = new Set(state.errors.map(e => e.error_type)).size;
    
    document.getElementById('total-errors').textContent = total;
    document.getElementById('unique-types').textContent = uniqueTypes;
}

/**
 * Show detailed error information
 * @param {Object} error - Error data
 */
function showErrorDetails(error) {
    const detailsDiv = document.getElementById('error-details');
    if (!detailsDiv) return;
    
    detailsDiv.innerHTML = `
        <div class="error-details">
            <div class="error-section">
                <div class="error-section-title">Error Details</div>
                <div class="error-section-content">
                    <strong>Type:</strong> ${error.error_type}<br>
                    <strong>Test:</strong> ${error.test_name}<br>
                    <strong>Root Cause:</strong> ${error.root_cause || 'Unknown'}<br>
                    <strong>Message:</strong> ${error.message}
                </div>
            </div>
            
            ${error.request ? `
                <div class="error-section">
                    <div class="error-section-title">Request</div>
                    <div class="error-section-content">
                        <strong>${error.request.method}</strong> ${error.request.url}<br>
                        ${error.request.headers ? `<strong>Headers:</strong> ${JSON.stringify(error.request.headers, null, 2)}` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${error.response ? `
                <div class="error-section">
                    <div class="error-section-title">Response</div>
                    <div class="error-section-content">
                        <strong>Status:</strong> ${error.response.status_code}<br>
                        ${error.response.body ? `<strong>Body:</strong> ${JSON.stringify(error.response.body, null, 2)}` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${error.suggestions && error.suggestions.length > 0 ? `
                <div class="error-section">
                    <div class="error-section-title">Fix Suggestions</div>
                    <ul class="fix-suggestions">
                        ${error.suggestions.map(s => `<li class="fix-suggestion">${s}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Handle API diff event
 * Updates diff list and badge counter
 * @param {Event} event - SSE event with diff data
 */
function handleAPIDiff(event) {
    const data = JSON.parse(event.data);
    state.diffs.push(...(data.changes || []));
    
    // Update badges
    const breaking = state.diffs.filter(d => d.breaking).length;
    const nonBreaking = state.diffs.length - breaking;
    
    document.getElementById('breaking-count').textContent = breaking;
    document.getElementById('non-breaking-count').textContent = nonBreaking;
    document.getElementById('total-changes').textContent = state.diffs.length;
    
    // Update diff list
    const changeList = document.getElementById('change-list');
    if (changeList.querySelector('.empty-state')) {
        changeList.innerHTML = '';
    }
    
    state.diffs.forEach(change => {
        const changeItem = createChangeItem(change);
        changeList.appendChild(changeItem);
    });
    
    addActivityLog('API Diff', `${data.changes?.length || 0} changes detected`);
}

/**
 * Create change item element
 * @param {Object} change - Change data
 * @returns {HTMLElement} Change item element
 */
function createChangeItem(change) {
    const item = document.createElement('div');
    item.className = `change-item ${change.breaking ? 'breaking' : 'non-breaking'}`;
    
    const typeClass = change.type.toLowerCase();
    
    item.innerHTML = `
        <span class="change-type ${typeClass}">${change.type}</span>
        <div class="change-path">${change.path}</div>
        <div class="change-description">${change.description}</div>
        ${change.recommendation ? `
            <div class="change-recommendation">
                <strong>Recommendation:</strong> ${change.recommendation}
            </div>
        ` : ''}
    `;
    
    return item;
}

/**
 * Handle anomaly event
 * Updates anomaly list and badge counter
 * @param {Event} event - SSE event with anomaly data
 */
function handleAnomaly(event) {
    const data = JSON.parse(event.data);
    state.anomalies.push(data);
    
    // Update badge
    const badge = document.getElementById('anomaly-badge');
    if (badge) badge.textContent = state.anomalies.length;
    
    // Add to anomaly list
    const anomalyList = document.getElementById('anomaly-list');
    if (anomalyList.querySelector('.empty-state')) {
        anomalyList.innerHTML = '';
    }
    
    const anomalyItem = createAnomalyItem(data);
    anomalyList.insertBefore(anomalyItem, anomalyList.firstChild);
    
    addActivityLog('Anomaly', `${data.severity}: ${data.type}`);
}

/**
 * Create anomaly item element
 * @param {Object} data - Anomaly data
 * @returns {HTMLElement} Anomaly item element
 */
function createAnomalyItem(data) {
    const item = document.createElement('div');
    item.className = `anomaly-item ${data.severity.toLowerCase()}`;
    
    item.innerHTML = `
        <div class="anomaly-header">
            <span class="anomaly-title">${data.endpoint || 'Unknown endpoint'}</span>
            <span class="anomaly-severity ${data.severity.toLowerCase()}">${data.severity}</span>
        </div>
        <div class="anomaly-description">${data.description}</div>
        <div class="anomaly-values">
            <div class="anomaly-value">
                <span class="anomaly-value-label">Expected:</span>
                <span class="anomaly-value-number">${data.expected}</span>
            </div>
            <div class="anomaly-value">
                <span class="anomaly-value-label">Actual:</span>
                <span class="anomaly-value-number">${data.actual}</span>
            </div>
        </div>
        <div class="anomaly-meta">
            <span>⏱ ${formatTimestamp(data.timestamp)}</span>
        </div>
    `;
    
    return item;
}

/**
 * Handle traffic event
 * Updates traffic list and badge counter
 * @param {Event} event - SSE event with traffic data
 */
function handleTraffic(event) {
    const data = JSON.parse(event.data);
    state.traffic.push(data);
    
    // Update badge
    const badge = document.getElementById('traffic-badge');
    if (badge) badge.textContent = state.traffic.length;
    
    // Add to traffic list
    const trafficList = document.getElementById('traffic-list');
    if (trafficList.querySelector('.empty-state')) {
        trafficList.innerHTML = '';
    }
    
    const trafficItem = createTrafficItem(data);
    trafficList.insertBefore(trafficItem, trafficList.firstChild);
    
    // Keep only last 100 items
    while (trafficList.children.length > 100) {
        trafficList.removeChild(trafficList.lastChild);
    }
}

/**
 * Create traffic item element
 * @param {Object} data - Traffic data
 * @returns {HTMLElement} Traffic item element
 */
function createTrafficItem(data) {
    const item = document.createElement('div');
    item.className = 'traffic-item';
    
    const statusClass = data.status_code < 400 ? 'success' : 'error';
    
    item.innerHTML = `
        <span class="traffic-method ${data.method.toLowerCase()}">${data.method}</span>
        <span class="traffic-url">${truncate(data.url, 50)}</span>
        <span class="traffic-status ${statusClass}">${data.status_code}</span>
        <span class="traffic-time">${formatTimestamp(data.timestamp)}</span>
    `;
    
    return item;
}

/**
 * Handle activity log event
 * @param {Event} event - SSE event
 */
function handleActivity(event) {
    const data = JSON.parse(event.data);
    addActivityLog(data.category || 'Activity', data.message);
}

/**
 * Add entry to activity log
 * @param {string} category - Activity category
 * @param {string} message - Activity message
 */
function addActivityLog(category, message) {
    const activityLog = document.getElementById('activity-log');
    if (!activityLog) return;
    
    const entry = document.createElement('div');
    entry.className = 'activity-entry';
    entry.innerHTML = `
        <span class="activity-time">${new Date().toLocaleTimeString()}</span>
        <span class="activity-category">${category}</span>
        <span class="activity-message">${message}</span>
    `;
    
    activityLog.insertBefore(entry, activityLog.firstChild);
    
    // Keep only last 50 entries
    while (activityLog.children.length > 50) {
        activityLog.removeChild(activityLog.lastChild);
    }
}

/**
 * Format timestamp to relative time
 * @param {string|number} timestamp - Timestamp to format
 * @returns {string} Formatted timestamp
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
 * @param {string} str - String to truncate
 * @param {number} length - Maximum length
 * @returns {string} Truncated string
 */
function truncate(str, length) {
    if (!str || str.length <= length) return str;
    return str.substring(0, length) + '...';
}

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
