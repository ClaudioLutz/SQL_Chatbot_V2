// Global application state
const appState = {
    currentQuery: {
        question: "",
        sql: "",
        results: {
            columns: [],
            rows: []
        },
        timestamp: null
    },
    analysis: {
        data: null,
        status: "idle", // idle | loading | success | error | too_large | insufficient_rows
        error: null
    },
    ui: {
        activeTab: "results"
    }
};

// State management functions
function resetAnalysisState() {
    appState.analysis = {
        data: null,
        status: "idle",
        error: null
    };
}

function updateAnalysisState(status, data = null, error = null) {
    appState.analysis.status = status;
    appState.analysis.data = data;
    appState.analysis.error = error;
}

function isAnalysisAvailable() {
    const { rows, columns } = appState.currentQuery.results;
    return rows.length >= 2 && columns.length >= 1;
}

// Tab switching functionality
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update UI state
    appState.ui.activeTab = tabName;
    
    // Update button active states
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // If switching to analysis tab and analysis not loaded, fetch it
    if (tabName === 'analysis') {
        if (appState.analysis.status === 'idle') {
            fetchAnalysis();
        } else if (appState.analysis.status === 'success') {
            // Analysis already loaded, just display it
            renderAnalysis(appState.analysis.data);
        }
    }
}

// Analysis API call functionality
async function fetchAnalysis() {
    // Check if analysis is available
    if (!isAnalysisAvailable()) {
        displayAnalysisMessage('insufficient_rows');
        return;
    }
    
    // Show loading indicator
    updateAnalysisState('loading');
    showLoadingIndicator();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                columns: appState.currentQuery.results.columns,
                rows: appState.currentQuery.results.rows
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide loading indicator
        hideLoadingIndicator();
        
        // Handle different response statuses
        if (data.status === 'success') {
            updateAnalysisState('success', data);
            renderAnalysis(data);
        } else if (data.status === 'too_large') {
            updateAnalysisState('too_large', null, data.message);
            displayAnalysisMessage('too_large', data.message);
        } else if (data.status === 'insufficient_rows') {
            updateAnalysisState('insufficient_rows', null, data.message);
            displayAnalysisMessage('insufficient_rows', data.message);
        } else {
            updateAnalysisState('error', null, data.message);
            displayAnalysisMessage('error', data.message);
        }
        
    } catch (error) {
        console.error('Analysis request failed:', error);
        hideLoadingIndicator();
        updateAnalysisState('error', null, error.message);
        displayAnalysisMessage('error', 'Failed to generate analysis. Please try again.');
    }
}

function showLoadingIndicator() {
    document.getElementById('analysis-loading').style.display = 'flex';
    document.getElementById('analysis-output').style.display = 'none';
    document.getElementById('analysis-error').style.display = 'none';
}

function hideLoadingIndicator() {
    document.getElementById('analysis-loading').style.display = 'none';
}

function displayAnalysisMessage(type, message = null) {
    const errorDiv = document.getElementById('analysis-error');
    const outputDiv = document.getElementById('analysis-output');
    
    outputDiv.style.display = 'none';
    errorDiv.style.display = 'block';
    
    const messages = {
        'insufficient_rows': 'Analysis requires at least 2 rows of data.',
        'too_large': message || 'Analysis unavailable for datasets exceeding 50,000 rows. Please refine your query for detailed statistics.',
        'error': message || 'Analysis could not be generated for this dataset.'
    };
    
    errorDiv.textContent = messages[type] || message;
    errorDiv.className = type === 'too_large' ? 'error-message info' : 'error-message';
}

// Analysis rendering functions
function renderAnalysis(data) {
    const outputDiv = document.getElementById('analysis-output');
    const errorDiv = document.getElementById('analysis-error');
    
    // Clear previous content
    outputDiv.innerHTML = '';
    errorDiv.style.display = 'none';
    outputDiv.style.display = 'block';
    
    // Create sections
    const html = `
        <div class="analysis-container">
            ${renderDatasetOverview(data)}
            ${renderVariableTypes(data.variable_types)}
            ${renderNumericStats(data.numeric_stats)}
            ${renderCardinality(data.cardinality)}
            ${renderMissingValues(data.missing_values)}
        </div>
    `;
    
    outputDiv.innerHTML = html;
}

function renderDatasetOverview(data) {
    return `
        <div class="analysis-section">
            <h3>Dataset Overview</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Rows</div>
                    <div class="stat-value">${data.row_count.toLocaleString()}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Columns</div>
                    <div class="stat-value">${data.column_count}</div>
                </div>
            </div>
        </div>
    `;
}

function renderVariableTypes(varTypes) {
    const typeEntries = Object.entries(varTypes)
        .filter(([_, count]) => count > 0)
        .map(([type, count]) => `
            <div class="stat-card">
                <div class="stat-label">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div class="stat-value">${count}</div>
            </div>
        `).join('');
    
    return `
        <div class="analysis-section">
            <h3>Variable Types</h3>
            <div class="stats-grid">
                ${typeEntries}
            </div>
        </div>
    `;
}

function renderNumericStats(stats) {
    if (!stats || stats.length === 0) {
        return '<div class="analysis-section"><h3>Numeric Statistics</h3><p>No numeric columns found.</p></div>';
    }
    
    const rows = stats.map(stat => `
        <tr>
            <td><strong>${stat.column}</strong></td>
            <td>${stat.count}</td>
            <td>${formatNumber(stat.mean)}</td>
            <td>${formatNumber(stat.std)}</td>
            <td>${formatNumber(stat.min)}</td>
            <td>${formatNumber(stat.q25)}</td>
            <td>${formatNumber(stat.q50)}</td>
            <td>${formatNumber(stat.q75)}</td>
            <td>${formatNumber(stat.max)}</td>
        </tr>
    `).join('');
    
    return `
        <div class="analysis-section">
            <h3>Numeric Statistics</h3>
            <div style="overflow-x: auto;">
                <table class="analysis-table">
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>Count</th>
                            <th>Mean</th>
                            <th>Std Dev</th>
                            <th>Min</th>
                            <th>Q25</th>
                            <th>Median</th>
                            <th>Q75</th>
                            <th>Max</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function renderCardinality(cardinalityData) {
    const rows = cardinalityData.map(item => `
        <tr>
            <td><strong>${item.column}</strong></td>
            <td>${item.unique_count.toLocaleString()}</td>
            <td>${item.total_count.toLocaleString()}</td>
            <td>${((item.unique_count / item.total_count) * 100).toFixed(1)}%</td>
        </tr>
    `).join('');
    
    return `
        <div class="analysis-section">
            <h3>Cardinality (Unique Values)</h3>
            <table class="analysis-table">
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Unique Values</th>
                        <th>Total Values</th>
                        <th>Uniqueness</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;
}

function renderMissingValues(missingData) {
    const rows = missingData.map(item => {
        const hasNulls = item.null_count > 0;
        const rowClass = hasNulls ? 'style="background-color: #fff3cd;"' : '';
        return `
            <tr ${rowClass}>
                <td><strong>${item.column}</strong></td>
                <td>${item.null_count.toLocaleString()}</td>
                <td>${item.null_percentage.toFixed(2)}%</td>
                <td>${hasNulls ? '⚠️ Has nulls' : '✓ Complete'}</td>
            </tr>
        `;
    }).join('');
    
    return `
        <div class="analysis-section">
            <h3>Missing Values</h3>
            <table class="analysis-table">
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Null Count</th>
                        <th>Null %</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;
}

function formatNumber(value) {
    if (value === null || value === undefined) {
        return 'N/A';
    }
    if (Number.isInteger(value)) {
        return value.toLocaleString();
    }
    return value.toFixed(2);
}

// Existing query functionality with integration
document.addEventListener('DOMContentLoaded', () => {
    const submitBtn = document.getElementById('submit-btn');
    const questionInput = document.getElementById('question-input');
    const sqlQueryOutput = document.getElementById('sql-query-output');
    const resultsOutput = document.getElementById('results-output');

    // Initialize tabs
    initializeTabs();

    submitBtn.addEventListener('click', async () => {
        const question = questionInput.value;
        if (!question) {
            alert('Please enter a question.');
            return;
        }

        sqlQueryOutput.textContent = 'Generating SQL...';
        resultsOutput.innerHTML = '';

        // Reset analysis state for new query
        resetAnalysisState();

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Handle query success
            handleQuerySuccess(data, question);
            
        } catch (error) {
            sqlQueryOutput.textContent = 'An error occurred.';
            resultsOutput.innerHTML = `<p style="color: red;">${error.message}</p>`;
            console.error('Error:', error);
            
            // Disable analysis tab on error
            const analysisTabBtn = document.getElementById('analysis-tab-btn');
            analysisTabBtn.disabled = true;
            analysisTabBtn.title = 'No data available for analysis';
        }
    });

    function handleQuerySuccess(data, question) {
        // Display SQL query
        sqlQueryOutput.textContent = data.sql_query || "No SQL generated.";
        
        // Store results in state
        appState.currentQuery.results = {
            columns: data.results.columns || [],
            rows: data.results.rows || []
        };
        appState.currentQuery.sql = data.sql_query;
        appState.currentQuery.question = question;
        appState.currentQuery.timestamp = Date.now();
        
        // Display results in Results tab
        displayResults(data.results);
        
        // Enable/disable Analysis tab based on dataset size
        const analysisTabBtn = document.getElementById('analysis-tab-btn');
        if (isAnalysisAvailable()) {
            analysisTabBtn.disabled = false;
            analysisTabBtn.title = '';
        } else {
            analysisTabBtn.disabled = true;
            analysisTabBtn.title = 'Analysis requires at least 2 rows';
        }
        
        // Switch to Results tab (default)
        switchTab('results');
    }

    function displayResults(results) {
        if (results.error) {
            resultsOutput.innerHTML = `<p style="color: red;">Error: ${results.error}</p>`;
        } else if (!results.rows || results.rows.length === 0) {
            resultsOutput.innerHTML = '<p>Query returned no results.</p>';
        } else {
            resultsOutput.innerHTML = createTable(results.columns, results.rows);
        }
    }

    function createTable(columns, rows) {
        let table = '<table><thead><tr>';
        columns.forEach(col => {
            table += `<th>${col}</th>`;
        });
        table += '</tr></thead><tbody>';
        rows.forEach(row => {
            table += '<tr>';
            columns.forEach(col => {
                table += `<td>${row[col] !== null ? row[col] : 'NULL'}</td>`;
            });
            table += '</tr>';
        });
        table += '</tbody></table>';
        return table;
    }
});
