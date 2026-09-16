let currentResponse = null;
let trajectoryChart = null;

async function solveQuery() {
    const query = document.getElementById('query').value.trim();
    if (!query) {
        showError('Query is empty', 'Please enter a scientific scenario.');
        return;
    }

    hideError();
    showLoading(true);
    hideResults();

    try {
        const response = await fetch('/api/prototype', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            let errorMsg = `HTTP ${response.status}`;
            try {
                const errorBody = await response.json();
                if (errorBody.message) {
                    errorMsg = errorBody.message;
                }
                if (errorBody.details) {
                    errorMsg += ': ' + errorBody.details;
                }
            } catch (e) {
                // Use default error message
            }
            throw new Error(errorMsg);
        }

        currentResponse = await response.json();
        showLoading(false);

        if (currentResponse.result && !currentResponse.result.success) {
            showError('Solver Error', currentResponse.result.error || 'Unknown solver error');
            return;
        }

        renderResults();
    } catch (error) {
        showLoading(false);
        showError('Request Failed', error.message);
        console.error('Error:', error);
    }
}

function renderResults() {
    if (!currentResponse) return;

    const model = currentResponse.model;
    const result = currentResponse.result;

    renderModel(model);
    renderResult(result);
    showResults();
}

function renderModel(model) {
    // Domain and description
    document.getElementById('domain').textContent = model.domain || 'N/A';
    document.getElementById('description').textContent = model.description || 'No description';

    // Quantities
    const quantitiesList = document.getElementById('quantitiesList');
    quantitiesList.innerHTML = '';
    if (model.quantities && model.quantities.length > 0) {
        model.quantities.forEach(q => {
            const li = document.createElement('li');
            const value = q.value !== undefined && q.value !== null ? `${q.value} ${q.siUnit || ''}` : q.siUnit || '';
            li.innerHTML = `<span class="quantity-name">${q.name}</span> <span class="quantity-value">${value}</span>`;
            quantitiesList.appendChild(li);
        });
    } else {
        quantitiesList.innerHTML = '<li>No quantities</li>';
    }

    // Equations
    const equationsList = document.getElementById('equationsList');
    equationsList.innerHTML = '';
    if (model.equations && model.equations.length > 0) {
        model.equations.forEach(eq => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="quantity-name">${eq.lhs}</span> = <span class="quantity-value">${eq.rhs}</span>`;
            equationsList.appendChild(li);
        });
    } else {
        equationsList.innerHTML = '<li>No equations</li>';
    }

    // Initial conditions
    const icList = document.getElementById('icList');
    icList.innerHTML = '';
    if (model.initialConditions && Object.keys(model.initialConditions).length > 0) {
        Object.entries(model.initialConditions).forEach(([key, value]) => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="quantity-name">${key}</span> <span class="quantity-value">= ${value}</span>`;
            icList.appendChild(li);
        });
    } else {
        icList.innerHTML = '<li>No initial conditions</li>';
    }

    document.getElementById('modelPanel').classList.add('active');
}

function renderResult(result) {
    const summaryList = document.getElementById('summaryList');
    summaryList.innerHTML = '';

    if (result.summary && Object.keys(result.summary).length > 0) {
        Object.entries(result.summary).forEach(([key, value]) => {
            const li = document.createElement('li');
            const displayValue = typeof value === 'number' ? value.toFixed(6) : value;
            li.innerHTML = `<span class="quantity-name">${key}</span> <span class="quantity-value">= ${displayValue}</span>`;
            summaryList.appendChild(li);
        });
    } else {
        summaryList.innerHTML = '<li>No summary results</li>';
    }

    // Handle trajectory plotting
    const chartSection = document.getElementById('chartSection');
    if (result.trajectory && Object.keys(result.trajectory).length > 0) {
        chartSection.style.display = 'block';
        plotTrajectory(result.trajectory);
    } else {
        chartSection.style.display = 'none';
        if (trajectoryChart) {
            trajectoryChart.destroy();
            trajectoryChart = null;
        }
    }

    document.getElementById('resultPanel').classList.add('active');
}

function plotTrajectory(trajectory) {
    const canvas = document.getElementById('trajectoryChart');
    const ctx = canvas.getContext('2d');

    if (trajectoryChart) {
        trajectoryChart.destroy();
    }

    const keys = Object.keys(trajectory);
    if (keys.length < 2) {
        console.warn('Trajectory needs at least 2 dimensions to plot');
        return;
    }

    const xKey = keys[0];
    const yKey = keys[1];
    const xData = trajectory[xKey];
    const yData = trajectory[yKey];

    const chartData = {
        labels: xData.map((_, i) => i),
        datasets: [{
            label: `${yKey} vs ${xKey}`,
            data: xData.map((x, i) => ({ x, y: yData[i] })),
            borderColor: 'rgb(42, 82, 152)',
            backgroundColor: 'rgba(42, 82, 152, 0.1)',
            borderWidth: 2,
            pointRadius: 3,
            pointBackgroundColor: 'rgb(42, 82, 152)',
            pointBorderColor: 'white',
            pointBorderWidth: 1,
            tension: 0.2,
            fill: false,
            showLine: true,
        }]
    };

    trajectoryChart = new Chart(ctx, {
        type: 'scatter',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        font: { size: 12 },
                        color: '#333',
                    }
                },
                title: {
                    display: false,
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: xKey,
                        color: '#1e3c72',
                        font: { size: 12, weight: '600' }
                    },
                    ticks: { color: '#666' },
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }
                },
                y: {
                    title: {
                        display: true,
                        text: yKey,
                        color: '#1e3c72',
                        font: { size: 12, weight: '600' }
                    },
                    ticks: { color: '#666' },
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }
                }
            }
        }
    });
}

function exportCSV() {
    if (!currentResponse || !currentResponse.result.trajectory) {
        showError('No trajectory', 'Cannot export: no trajectory data available');
        return;
    }

    const trajectory = currentResponse.result.trajectory;
    const keys = Object.keys(trajectory);

    if (keys.length === 0) {
        showError('No trajectory', 'Cannot export: trajectory is empty');
        return;
    }

    // Build CSV header
    const header = keys.join(',');

    // Build CSV rows
    const maxLength = Math.max(...keys.map(k => trajectory[k].length));
    const rows = [];
    for (let i = 0; i < maxLength; i++) {
        const row = keys.map(k => {
            const value = trajectory[k][i];
            return value !== undefined ? value : '';
        });
        rows.push(row.join(','));
    }

    const csv = [header, ...rows].join('\n');
    downloadFile(csv, 'trajectory.csv', 'text/csv');
    showSuccess('CSV exported successfully');
}

function exportPNG() {
    if (!trajectoryChart || !trajectoryChart.canvas) {
        showError('No chart', 'Cannot export: chart not rendered');
        return;
    }

    const canvas = trajectoryChart.canvas;
    const link = document.createElement('a');
    link.href = canvas.toDataURL('image/png');
    link.download = 'trajectory.png';
    link.click();
    showSuccess('PNG exported successfully');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

function showLoading(show) {
    const loadingEl = document.getElementById('loading');
    const solveBtn = document.getElementById('solveBtn');
    if (show) {
        loadingEl.classList.add('active');
        solveBtn.disabled = true;
    } else {
        loadingEl.classList.remove('active');
        solveBtn.disabled = false;
    }
}

function showError(title, message) {
    const errorPanel = document.getElementById('errorPanel');
    document.getElementById('errorMessage').textContent = message;
    errorPanel.querySelector('h3').textContent = title;
    errorPanel.classList.add('active');
}

function hideError() {
    document.getElementById('errorPanel').classList.remove('active');
}

function showSuccess(message) {
    const successEl = document.getElementById('successMessage');
    successEl.textContent = '✓ ' + message;
    successEl.classList.add('active');
    setTimeout(() => {
        successEl.classList.remove('active');
    }, 3000);
}

function showResults() {
    document.getElementById('resultsContainer').style.display = 'grid';
}

function hideResults() {
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('modelPanel').classList.remove('active');
    document.getElementById('resultPanel').classList.remove('active');
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');

    // Load history if switching to history tab
    if (tabName === 'history') {
        loadHistory();
    }
}

async function loadHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '<div class="history-empty">Loading history...</div>';

    try {
        const response = await fetch('/api/prototype/history?page=0&pageSize=50');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const items = data.content || [];

        if (items.length === 0) {
            historyList.innerHTML = '<div class="history-empty">No prototypes yet. Solve a query to get started!</div>';
            return;
        }

        historyList.innerHTML = '';
        items.forEach(item => {
            const statusClass = item.success ? 'success' : 'error';
            const statusText = item.success ? '✓ Success' : '✗ Error';
            const datetime = new Date(item.createdAt).toLocaleString();

            const itemEl = document.createElement('div');
            itemEl.className = 'history-item';
            itemEl.innerHTML = `
                <div class="history-item-header">
                    <div class="history-item-query">${escapeHtml(item.query.substring(0, 100))}</div>
                </div>
                <div class="history-item-meta">
                    <span class="history-domain">${escapeHtml(item.domain)}</span>
                    <span class="history-status ${statusClass}">${statusText}</span>
                    <span>${datetime}</span>
                </div>
            `;
            historyList.appendChild(itemEl);
        });
    } catch (error) {
        historyList.innerHTML = `<div class="history-empty">Error loading history: ${error.message}</div>`;
    }
}

function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Allow Enter key to trigger solve
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('query').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            solveQuery();
        }
    });
});
