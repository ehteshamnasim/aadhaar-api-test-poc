// SSE Connection
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
  } else if (status === 'triggered') {
    element.style.background = '#ff9800';
    element.style.color = 'white';
    element.textContent = '🚀 Triggered';
  } else {
    element.style.background = '#e0e0e0';
    element.style.color = '#666';
    element.textContent = status || 'Pending';
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

  // Reset badges
  updateBadge('parse-status', 'Pending');
  updateBadge('gen-status', 'Pending');
  updateBadge('syntax-check', 'Pending');
  updateBadge('import-check', 'Pending');
  updateBadge('validation-status', 'Pending');
  updateBadge('git-commit', 'Pending');
  updateBadge('git-push', 'Pending');
  updateBadge('cicd-status', 'Not Started');

  // Reset progress
  document.getElementById('gen-progress').style.width = '0%';

  // Reset coverage
  updateCoverage(0);

  // Hide comparison
  document.getElementById('comparison-section').style.display = 'none';

  // Clear log
  document.getElementById('log').innerHTML = '';

  // Reset status
  document.getElementById('status').textContent = 'Dashboard reset';

  addLog('Dashboard reset - ready for new POC run', 'info');
}

// Handle SSE events
eventSource.onmessage = function (event) {
  const data = JSON.parse(event.data);
  updateTimestamp();

  switch (data.type) {
    case 'connected':
      addLog('Connected to dashboard', 'info');
      break;

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

// Enhanced event handling for complete solution

case 'execute':
    // FIXED: Proper handling of all test counts
    const passed = data.passed || 0;
    const failed = data.failed || 0;
    const skipped = data.skipped || 0;
    const total = data.total || 0;
    
    document.getElementById('tests-passed').textContent = passed;
    document.getElementById('tests-failed').textContent = failed;
    document.getElementById('tests-total').textContent = total;
    
    // Show skipped if present
    const skippedEl = document.getElementById('tests-skipped');
    if (skippedEl) {
        skippedEl.textContent = skipped;
        skippedEl.style.display = skipped > 0 ? 'block' : 'none';
    }
    
    // Validate counts
    const calculatedTotal = passed + failed + skipped;
    if (calculatedTotal !== total && total > 0) {
        console.warn(`Count mismatch: ${passed}+${failed}+${skipped}=${calculatedTotal} but total=${total}`);
    }
    
    // Show test details
    if (data.details && data.details.length > 0) {
        const detailsCard = document.getElementById('test-details-card');
        if (detailsCard) {
            detailsCard.style.display = 'block';
            
            const detailsList = document.getElementById('test-details-list');
            detailsList.innerHTML = '';
            
            data.details.forEach((detail, index) => {
                const detailDiv = document.createElement('div');
                detailDiv.className = detail.passed ? 'test-detail-item passed' : 'test-detail-item failed';
                
                const icon = detail.passed ? '✅' : '❌';
                const statusClass = detail.passed ? 'status-passed' : 'status-failed';
                const statusText = detail.passed ? 'PASSED' : 'FAILED';
                
                detailDiv.innerHTML = `
                    <div class="test-detail-header">
                        <span class="test-icon">${icon}</span>
                        <span class="test-name">${detail.name}</span>
                        <span class="test-status ${statusClass}">${statusText}</span>
                    </div>
                    <div class="test-reason">${detail.reason}</div>
                `;
                detailsList.appendChild(detailDiv);
            });
            
            addLog(`Test execution: ${passed} passed, ${failed} failed`, failed === 0 ? 'success' : 'error');
        }
    } else {
        const detailsCard = document.getElementById('test-details-card');
        if (detailsCard) {
            detailsCard.style.display = 'none';
        }
    }
    
    break;
case 'clear':
    // Clear test details when resetting
    document.getElementById('test-details-card').style.display = 'none';
    resetDashboard();
    addLog('Dashboard cleared for new POC run', 'info');
    break;


    case 'coverage':
      const percentage = data.percentage || 0;
      updateCoverage(percentage);
      addLog(`Coverage: ${percentage}%`, percentage >= 85 ? 'success' : 'info');
      break;

    case 'contract':
      document.getElementById('contracts-tested').textContent = data.total || 0;
      document.getElementById('contracts-passed').textContent = data.passed || 0;
      document.getElementById('contracts-failed').textContent = data.failed || 0;

      if (data.status === 'running') {
        addLog(`Running contract tests for ${data.total || 0} endpoints...`, 'info');
      } else if (data.status === 'completed') {
        const status = data.failed === 0 ? 'success' : 'error';
        addLog(`Contract tests: ${data.passed || 0}/${data.total || 0} passed`, status);
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

    case 'clear':
      // Clear dashboard for new run
      resetDashboard();
      addLog('Dashboard cleared for new POC run', 'info');
      break;

    case 'completion':
      // POC completed - show final message
      addLog(`✅ POC completed - ${data.test_file} generated`, 'success');
      addLog(`Duration: ${data.duration}s, Coverage: ${data.coverage}%`, 'success');
      break;
    case 'error':
      addLog(`Error: ${data.message}`, 'error');
      break;
  }
};

eventSource.onerror = function (error) {
  console.error('SSE Error:', error);
  document.getElementById('status').textContent = 'Connection lost';
  addLog('Connection to server lost. Retrying...', 'error');
};

// Initialize
updateTimestamp();
setInterval(updateTimestamp, 1000);
addLog('Dashboard initialized', 'info');
