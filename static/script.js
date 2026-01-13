// PhishGuard AI - Enhanced JavaScript with XGBoost, SHAP, Charts, History, Batch Analysis

// Global state
let modelChart = null;
let riskPieChart = null;
let batchResults = [];
let currentAnalysisData = null;

// Initialize on page load
// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    loadTheme();
    loadHistory();
    updateHistoryCount();

    // Attach event listeners
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeURL);
    }

    const urlInput = document.getElementById('url-input');
    if (urlInput) {
        urlInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                analyzeURL();
            }
        });
    }
});

// ================== Theme Toggle ==================
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    if (newTheme === 'light') {
        document.body.setAttribute('data-theme', 'light');
        document.getElementById('theme-icon').className = 'fas fa-sun';
    } else {
        document.body.removeAttribute('data-theme');
        document.getElementById('theme-icon').className = 'fas fa-moon';
    }
    
    localStorage.setItem('theme', newTheme);
    
    // Refresh charts if they exist
    if (currentAnalysisData) {
        renderCharts(currentAnalysisData);
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.setAttribute('data-theme', 'light');
        document.getElementById('theme-icon').className = 'fas fa-sun';
    }
}

// ================== History Sidebar ==================
function toggleHistory() {
    const sidebar = document.getElementById('history-sidebar');
    sidebar.classList.toggle('hidden');
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    const historyList = document.getElementById('history-list');
    
    if (history.length === 0) {
        historyList.innerHTML = '<p class="history-empty">No scans yet</p>';
        return;
    }
    
    historyList.innerHTML = '';
    history.slice(0, 20).reverse().forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.onclick = () => displayHistoryItem(item);
        
        const riskClass = item.probability >= 0.75 ? 'high' : 
                         item.probability >= 0.50 ? 'medium' : 'low';
        
        div.innerHTML = `
            <div class="history-item-time">${new Date(item.timestamp).toLocaleString()}</div>
            <div class="history-item-url">${item.url}</div>
            <span class="history-item-badge ${riskClass}">${(item.probability * 100).toFixed(0)}% Risk</span>
        `;
        historyList.appendChild(div);
    });
}

function saveToHistory(data) {
    const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    
    const historyItem = {
        timestamp: Date.now(),
        url: data.url,
        probability: data.overall.probability,
        fullData: data
    };
    
    history.push(historyItem);
    
    // Keep only last 20
    if (history.length > 20) {
        history.shift();
    }
    
    localStorage.setItem('scanHistory', JSON.stringify(history));
    loadHistory();
    updateHistoryCount();
}

function displayHistoryItem(item) {
    displayResults(item.fullData);
    toggleHistory(); // Close sidebar
    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
}

function clearHistory() {
    if (confirm('Clear all scan history?')) {
        localStorage.removeItem('scanHistory');
        loadHistory();
        updateHistoryCount();
    }
}

function updateHistoryCount() {
    const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    document.getElementById('history-count').textContent = history.length;
}

// ================== URL Analysis ==================
async function analyzeURL() {
    const urlInput = document.getElementById('url-input');
    const url = urlInput.value.trim();
    const btn = document.getElementById('analyze-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');

    if (!url) {
        showError('Please enter a target URL for inspection.');
        return;
    }

    // Reset UI
    hideError();
    document.getElementById('results-section').classList.add('hidden');

    // Show Loading State
    if (btnText) btnText.classList.add('hidden');
    if (btnLoader) btnLoader.classList.remove('hidden');
    btn.disabled = true;

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'error') {
            showError(data.error);
        } else {
            currentAnalysisData = data;
            displayResults(data);
            saveToHistory(data);
        }
    } catch (error) {
        showError('Analysis failed: ' + error.message);
        console.error('Analysis error:', error);
    } finally {
        // Reset Button
        if (btnText) btnText.classList.remove('hidden');
        if (btnLoader) btnLoader.classList.add('hidden');
        btn.disabled = false;
    }
}

function displayResults(data) {
    // 1. URL Display
    document.getElementById('result-url-text').textContent = data.url;

    // 2. Semi-Circle Gauge Logic (use ensemble probability)
    const probability = data.ensemble ? data.ensemble.probability : data.overall.probability;
    const percent = Math.round(probability * 100);
    document.getElementById('risk-score-value').textContent = percent + '%';

    const fill = document.getElementById('risk-gauge-fill');
    const rotation = (percent / 100) * 180;
    fill.style.transform = `rotate(${rotation - 180}deg)`;

    // Color logic
    let colorVar = '--neon-green';
    let verdict = 'LEGITIMATE';
    let riskClass = 'low';

    if (percent >= 75) {
        colorVar = '--neon-red';
        verdict = 'PHISHING';
        riskClass = 'high';
    } else if (percent >= 50) {
        colorVar = '--neon-yellow';
        verdict = 'SUSPICIOUS';
        riskClass = 'medium';
    } else if (percent >= 25) {
        colorVar = '--primary';
        verdict = 'CAUTION';
        riskClass = 'medium';
    }

    fill.style.background = `var(${colorVar})`;

    const badge = document.getElementById('risk-badge');
    badge.textContent = `VERDICT: ${verdict}`;
    badge.className = `risk-badge ${riskClass}`;

    // 3. Summary Section
    const predText = document.getElementById('overall-prediction');
    predText.textContent = data.ensemble ? data.ensemble.prediction : data.overall.prediction;
    predText.style.color = `var(${colorVar})`;

    document.getElementById('analysis-reasoning').textContent =
        `System analysis confirms a ${percent}% probability of ${verdict.toLowerCase()} intent based on ensemble model predictions and URL structure.`;

    // Threat Tag
    const tagBox = document.getElementById('threat-tag-box');
    if (percent >= 50 || (data.threat_intelligence && data.threat_intelligence.threat_found)) {
        tagBox.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Dangerous Pattern Detected';
        tagBox.style.color = 'var(--neon-red)';
    } else {
        tagBox.innerHTML = '<i class="fas fa-check-circle"></i> No Threats Detected';
        tagBox.style.color = 'var(--neon-green)';
    }

    // Mini Models Display
    document.getElementById('lr-mini-val').textContent = data.models.logistic_regression.prediction;
    document.getElementById('rf-mini-val').textContent = data.models.random_forest.prediction;

    if (data.models.xgboost) {
        document.getElementById('xgb-mini-val').textContent = data.models.xgboost.prediction;
    }

    if (data.ensemble) {
        document.getElementById('ensemble-mini-val').textContent = data.ensemble.prediction;
    }

    // 4. Render Charts
    renderCharts(data);

    // 5. Render SHAP Analysis
    renderSHAP(data);

    // 5.1 Render LIME Analysis
    renderLIME(data);

    // 6. Technical Details
    if (data.advanced_analysis) {
        const adv = data.advanced_analysis;
        document.getElementById('redirects-content').textContent = adv.redirects?.redirects?.length > 0 ? `${adv.redirects.redirects.length} hops` : 'Direct Link';
        document.getElementById('ssl-content').innerHTML = adv.ssl_certificate?.certificate_valid ? '<span style="color:var(--neon-green)">Encrypted</span>' : '<span style="color:var(--neon-red)">Unencrypted</span>';
        document.getElementById('whois-content').textContent = adv.whois?.days_old ? `${adv.whois.days_old} days old` : 'Unknown Age';

        if (data.link_threats) {
            let ltText = `Score: ${data.link_threats.threat_score}/100`;
            if (data.link_threats.threats_found?.length > 0) {
                ltText += ` (${data.link_threats.threats_found[0]})`;
            }
            document.getElementById('link-threats-content').textContent = ltText;
        }
    }

    // Reveal
    document.getElementById('results-section').classList.remove('hidden');
    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
}

// ================== Chart.js Rendering ==================
function renderCharts(data) {
    // Destroy existing charts
    if (modelChart) modelChart.destroy();
    if (riskPieChart) riskPieChart.destroy();

    const isDark = !document.body.hasAttribute('data-theme') || document.body.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#f8fafc' : '#0f172a';
    const gridColor = isDark ? 'rgba(51, 65, 85, 0.5)' : 'rgba(226, 232, 240, 0.5)';

    // Model Confidences Bar Chart
    const modelCtx = document.getElementById('model-chart');
    if (modelCtx) {
        const modelData = {
            labels: ['LR', 'RF', 'XGBoost', 'Ensemble'],
            datasets: [{
                label: 'Confidence (%)',
                data: [
                    (data.models.logistic_regression.probability * 100).toFixed(1),
                    (data.models.random_forest.probability * 100).toFixed(1),
                    data.models.xgboost ? (data.models.xgboost.probability * 100).toFixed(1) : 0,
                    data.ensemble ? (data.ensemble.probability * 100).toFixed(1) : 0
                ],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(168, 85, 247, 0.7)',
                    'rgba(236, 72, 153, 0.7)',
                    'rgba(34, 197, 94, 0.7)'
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(168, 85, 247)',
                    'rgb(236, 72, 153)',
                    'rgb(34, 197, 94)'
                ],
                borderWidth: 2
            }]
        };

        modelChart = new Chart(modelCtx, {
            type: 'bar',
            data: modelData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: textColor,
                            callback: function (value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: gridColor
                        }
                    },
                    x: {
                        ticks: {
                            color: textColor
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Risk Factor Breakdown Pie Chart
    const pieCtx = document.getElementById('risk-pie-chart');
    if (pieCtx) {
        // Calculate breakdown based on warning signs and threats
        let lexicalScore = data.warning_signs ? data.warning_signs.length * 5 : 10;
        let threatIntelScore = (data.threat_intelligence && data.threat_intelligence.threat_found) ? 30 : 10;
        let advancedScore = data.advanced_analysis ? 20 : 10;
        let mlScore = 40;

        const total = lexicalScore + threatIntelScore + advancedScore + mlScore;

        const pieData = {
            labels: ['ML Models', 'Lexical Features', 'Threat Intel', 'Advanced Checks'],
            datasets: [{
                data: [
                    ((mlScore / total) * 100).toFixed(1),
                    ((lexicalScore / total) * 100).toFixed(1),
                    ((threatIntelScore / total) * 100).toFixed(1),
                    ((advancedScore / total) * 100).toFixed(1)
                ],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(234, 179, 8, 0.8)',
                    'rgba(168, 85, 247, 0.8)'
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(239, 68, 68)',
                    'rgb(234, 179, 8)',
                    'rgb(168, 85, 247)'
                ],
                borderWidth: 2
            }]
        };

        riskPieChart = new Chart(pieCtx, {
            type: 'doughnut',
            data: pieData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: textColor,
                            padding: 15,
                            font: {
                                size: 11
                            }
                        }
                    }
                }
            }
        });
    }
}

// ================== SHAP Rendering ==================
function renderSHAP(data) {
    const container = document.getElementById('shap-container');

    if (!data.shap_analysis || !data.shap_analysis.top_reasons || data.shap_analysis.top_reasons.length === 0) {
        container.innerHTML = '<div class="placeholder-chart">SHAP analysis not available for this URL</div>';
        return;
    }

    container.innerHTML = '';

    data.shap_analysis.top_reasons.forEach(reason => {
        const row = document.createElement('div');
        row.className = 'shap-feature-row';

        const featureName = reason.feature.replace(/_/g, ' ').replace(/\w\S*/g, (txt) =>
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        );

        const absImpact = Math.abs(reason.impact);
        const impactPercent = Math.min(absImpact * 100, 100); // Scale for visualization
        const impactClass = reason.direction === 'phishing' ? 'positive' : 'negative';

        row.innerHTML = `
            <div class="shap-feature-name">${featureName}</div>
            <div class="shap-impact-bar">
                <div class="shap-impact-fill ${impactClass}" style="width: ${impactPercent}%">
                    ${reason.impact.toFixed(3)}
                </div>
            </div>
            <div class="shap-direction ${reason.direction}">
                ${reason.direction === 'phishing' ? '<i class="fas fa-arrow-up"></i>' : '<i class="fas fa-arrow-down"></i>'}
                ${reason.direction}
            </div>
        `;

        container.appendChild(row);
    });

}

// ================== LIME Rendering ==================
function renderLIME(data) {
    // If we want a separate container, we should create one in index.html
    // For now, let's append to the SHAP container or create a new section if requested
    // The user asked to render lime_analysis as a colored list

    // Let's create a dedicated section if it doesn't exist, or reuse SHAP container for now
    // But better to add a LIME section. Since I can't edit index.html easily without seeing it,
    // I'll append a LIME header + content to the existing results area or 'shap-container' if suitable.
    // Actually, I should check if there is a 'lime-container'. 
    // Assuming I can't modify index.html right now without a task for it, 
    // I will dynamically insert a LIME section after the SHAP section if needed.

    // But let's look for a container. The user didn't ask to modify index.html.
    // I will assume there is a place or I will inject it.
    // Let's inject it into the 'technical-details' or create a new block after SHAP.

    let limeContainer = document.getElementById('lime-container');
    if (!limeContainer) {
        // Create it dynamically after shap-container
        const shapContainer = document.getElementById('shap-container');
        if (shapContainer && shapContainer.parentNode) {
            const wrapper = document.createElement('div');
            wrapper.className = 'analysis-card'; // Reuse style
            wrapper.style.marginTop = '20px';
            wrapper.innerHTML = '<h3><i class="fas fa-search-plus"></i> Local Explanation (LIME)</h3><div id="lime-container" class="shap-container"></div>';
            shapContainer.parentNode.parentNode.insertBefore(wrapper, shapContainer.parentNode.nextSibling);
            limeContainer = document.getElementById('lime-container');
        }
    }

    if (!limeContainer) return; // Fail safe

    if (!data.lime_analysis || !data.lime_analysis.top_contributing_features) {
        limeContainer.innerHTML = '<div class="placeholder-chart">LIME analysis not available</div>';
        return;
    }

    limeContainer.innerHTML = '';

    data.lime_analysis.top_contributing_features.forEach(item => {
        const row = document.createElement('div');
        row.className = 'shap-feature-row'; // Reuse SHAP styling for consistency

        const featureName = item.feature;
        const weight = item.weight;
        const impactClass = weight > 0 ? 'positive' : 'negative'; // Red if > 0 (Phishing risk), Green if < 0
        const impactPercent = Math.min(Math.abs(weight) * 300, 100); // Scale up for visibility

        row.innerHTML = `
            <div class="shap-feature-name" style="font-family: monospace; font-size: 0.9em;">${featureName}</div>
            <div class="shap-impact-bar">
                <div class="shap-impact-fill ${impactClass}" style="width: ${impactPercent}%">
                    ${weight.toFixed(3)}
                </div>
            </div>
            <div class="shap-direction ${item.direction}">
                 ${weight > 0 ? '<i class="fas fa-arrow-up"></i> Risk' : '<i class="fas fa-arrow-down"></i> Safe'}
            </div>
        `;
        limeContainer.appendChild(row);
    });
}

// ================== Batch Analysis ==================
function switchMode(mode) {
    const singlePill = document.getElementById('single-pill');
    const batchPill = document.getElementById('batch-pill');
    const inputSection = document.querySelector('.input-section');
    const batchSection = document.getElementById('batch-section');
    const resultsSection = document.getElementById('results-section');

    if (mode === 'single') {
        singlePill.classList.add('active');
        batchPill.classList.remove('active');
        inputSection.classList.remove('hidden');
        batchSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
    } else {
        singlePill.classList.remove('active');
        batchPill.classList.add('active');
        inputSection.classList.add('hidden');
        batchSection.classList.remove('hidden');
        resultsSection.classList.add('hidden');
    }
}

async function analyzeBatch() {
    const textarea = document.getElementById('batch-input');
    const urls = textarea.value.split('\n').filter(u => u.trim()).map(u => u.trim());

    if (urls.length === 0) {
        alert('Please enter at least one URL');
        return;
    }

    if (urls.length > 20) {
        alert('Maximum 20 URLs allowed per batch');
        return;
    }

    batchResults = [];
    const tbody = document.getElementById('batch-table-body');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">Analyzing...</td></tr>';
    document.getElementById('batch-results').classList.remove('hidden');

    for (let i = 0; i < urls.length; i++) {
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: urls[i] })
            });

            const data = await response.json();

            if (data.status === 'success') {
                const prob = data.ensemble ? data.ensemble.probability : data.overall.probability;
                const verdict = data.ensemble ? data.ensemble.prediction : data.overall.prediction;

                batchResults.push({
                    url: urls[i],
                    verdict: verdict,
                    risk: (prob * 100).toFixed(1) + '%',
                    ensemble: data.ensemble ? data.ensemble.confidence : data.overall.confidence,
                    riskLevel: prob >= 0.75 ? 'high' : prob >= 0.5 ? 'medium' : 'low'
                });
            } else {
                batchResults.push({
                    url: urls[i],
                    verdict: 'ERROR',
                    risk: 'N/A',
                    ensemble: 'N/A',
                    riskLevel: 'low'
                });
            }

            // Update table
            updateBatchTable();

        } catch (error) {
            batchResults.push({
                url: urls[i],
                verdict: 'ERROR',
                risk: 'N/A',
                ensemble: 'N/A',
                riskLevel: 'low'
            });
            updateBatchTable();
        }
    }

    document.getElementById('export-batch-btn').disabled = false;
}

function updateBatchTable() {
    const tbody = document.getElementById('batch-table-body');
    tbody.innerHTML = '';

    batchResults.forEach((result, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td class="batch-url-cell" title="${result.url}">${result.url}</td>
            <td><span class="history-item-badge ${result.riskLevel}">${result.verdict}</span></td>
            <td>${result.risk}</td>
            <td>${result.ensemble}</td>
        `;
        tbody.appendChild(row);
    });
}

function exportBatchResults() {
    if (batchResults.length === 0) return;

    let csv = 'URL,Verdict,Risk Probability,Ensemble Confidence\n';
    batchResults.forEach(result => {
        csv += `"${result.url}","${result.verdict}","${result.risk}","${result.ensemble}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `phishguard_batch_${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// ================== Advanced Toggle ==================
function toggleAdvanced() {
    const grid = document.getElementById('advanced-details');
    const btn = document.getElementById('toggle-details-btn');
    const isHidden = grid.classList.toggle('hidden');

    if (btn) {
        if (!isHidden) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    }
}

// ================== Error Handling ==================
function showError(msg) {
    const errDiv = document.getElementById('error-message');
    errDiv.textContent = msg;
    errDiv.classList.remove('hidden');
}

function hideError() {
    const errDiv = document.getElementById('error-message');
    errDiv.classList.add('hidden');
}


