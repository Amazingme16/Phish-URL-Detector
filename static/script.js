// Main JavaScript for P URL D - UI Redo 2.0

function analyzeURL() {
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
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    btn.disabled = true;

    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    })
        .then(response => response.json())
        .then(data => {
            // Reset Button
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
            btn.disabled = false;

            if (data.status === 'error') {
                showError(data.error);
                return;
            }

            displayResults(data);
        })
        .catch(error => {
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
            btn.disabled = false;
            showError('Analysis failed: ' + error.message);
        });
}

function displayResults(data) {
    // 1. URL Display
    document.getElementById('result-url-text').textContent = data.url;

    // 2. Semi-Circle Gauge Logic
    const probability = data.overall.probability;
    const percent = Math.round(probability * 100);
    document.getElementById('risk-score-value').textContent = percent + '%';

    const fill = document.getElementById('risk-gauge-fill');
    // Calculate rotation: 0% is -180deg (all red/start), 100% is 0deg (all way across)
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
    predText.textContent = data.overall.prediction;
    predText.style.color = `var(${colorVar})`;

    document.getElementById('analysis-reasoning').textContent = data.overall.logic_summary ||
        `System analysis confirms a ${percent}% probability of ${verdict.toLowerCase()} intent based on URL structure and external reputation.`;

    // Threat Tag
    const tagBox = document.getElementById('threat-tag-box');
    if (percent >= 50 || (data.threat_intelligence && data.threat_intelligence.threat_found)) {
        tagBox.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Dangerous Pattern Detected';
        tagBox.style.color = 'var(--neon-red)';
    } else {
        tagBox.innerHTML = '<i class="fas fa-check-circle"></i> No Threats Detected';
        tagBox.style.color = 'var(--neon-green)';
    }

    // Mini Models
    document.getElementById('lr-mini-val').textContent = data.models.logistic_regression.prediction;
    document.getElementById('rf-mini-val').textContent = data.models.random_forest.prediction;

    // 4. Feature Chart (Contribution Weights)
    renderFeatureChart(data.features || {});

    // 5. Advanced Flags (Warning List) populates the summary reasoning or flags

    // 6. Technical Details
    if (data.advanced_analysis) {
        const adv = data.advanced_analysis;
        document.getElementById('redirects-content').textContent = adv.redirects?.redirects?.length > 0 ? `${adv.redirects.redirects.length} hops` : 'Direct Link';
        document.getElementById('ssl-content').innerHTML = adv.ssl_certificate?.certificate_valid ? '<span style="color:var(--neon-green)">Encrypted</span>' : '<span style="color:var(--neon-red)">Unencrypted</span>';
        document.getElementById('whois-content').textContent = adv.whois?.days_old ? `${adv.whois.days_old} days old` : 'Unknown Age';

        // Link Threats Detailed
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

function renderFeatureChart(features) {
    const container = document.getElementById('feature-chart-container');
    container.innerHTML = '';

    const entries = Object.entries(features)
        .filter(([k, v]) => !['status', 'url', 'prediction', 'probability'].includes(k))
        .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
        .slice(0, 10);

    if (entries.length === 0) {
        container.innerHTML = '<div class="placeholder-chart">Feature data unavailable</div>';
        return;
    }

    entries.forEach(([name, weight]) => {
        const row = document.createElement('div');
        row.className = 'feature-bar-row';

        const cleanName = name.replace(/_/g, ' ').replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
        const absWeight = Math.min(Math.abs(weight) * 50, 100); // Scale multiplier for visibility
        const color = weight > 0 ? 'var(--neon-red)' : 'var(--neon-green)';

        row.innerHTML = `
            <div class="feature-name" title="${name}">${cleanName}</div>
            <div class="feature-bar-bg">
                <div class="feature-bar-fill" style="width: ${absWeight}%; background: ${color}"></div>
            </div>
            <div class="feature-val">${weight.toFixed(2)}</div>
        `;
        container.appendChild(row);
    });
}

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

function showError(msg) {
    const errDiv = document.getElementById('error-message');
    errDiv.textContent = msg;
    errDiv.classList.remove('hidden');
}

function hideError() {
    const errDiv = document.getElementById('error-message');
    errDiv.classList.add('hidden');
}

document.getElementById('url-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        analyzeURL();
    }
});
