// Global application state
const appState = {
    sql: {
        mode: "auto", // auto | manual
        query: "",
        originalGenerated: "",
        lastSuccessfulQuery: "",
        isEdited: false,
        isValid: false,
        validationMessage: "",
        lastExecutionTime: null
    },
    currentQuery: {
        question: "",
        sql: "",
        results: {
            columns: [],
            rows: []
        },
        timestamp: null,
        executionMode: "auto", // auto | manual
        executionTimeMs: 0,
        rowCount: 0
    },
    analysis: {
        data: null,
        status: "idle", // idle | loading | success | error | too_large | insufficient_rows
        error: null
    },
    visualization: {
        isAvailable: false,
        plotlyLoaded: false,
        status: "idle", // idle | loading | success | error
        error: null,
        chartType: null,
        xColumn: null,
        yColumn: null,
        columnTypes: {},
        chartData: null,
        isSampled: false,
        originalRowCount: null,
        sampledRowCount: null
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
    
    // If switching to visualizations tab, initialize it
    if (tabName === 'visualizations') {
        initializeVisualizationTab();
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

// ============================================
// MANUAL SQL EDITING FUNCTIONS
// ============================================

// State persistence
function saveToSessionStorage() {
    sessionStorage.setItem('sql_state', JSON.stringify({
        mode: appState.sql.mode,
        query: appState.sql.query,
        originalGenerated: appState.sql.originalGenerated
    }));
}

function restoreFromSessionStorage() {
    const saved = sessionStorage.getItem('sql_state');
    if (saved) {
        try {
            const state = JSON.parse(saved);
            appState.sql.mode = state.mode || 'auto';
            appState.sql.query = state.query || '';
            appState.sql.originalGenerated = state.originalGenerated || '';
            return true;
        } catch (e) {
            console.error('Error restoring state:', e);
            return false;
        }
    }
    return false;
}

function getQueryHash(sql) {
    // Simple hash for query identity
    return btoa(sql).substring(0, 16);
}

// SQL validation
function validateSQL(sql) {
    const trimmed = sql.trim();
    
    if (!trimmed) {
        return {
            isValid: false,
            message: ''
        };
    }
    
    const sqlLower = trimmed.toLowerCase();
    
    // Must start with SELECT or WITH
    if (!sqlLower.startsWith('select') && !sqlLower.startsWith('with')) {
        return {
            isValid: false,
            message: '❌ Only SELECT statements allowed'
        };
    }
    
    // Check for dangerous keywords
    const dangerous = ['drop ', 'delete ', 'update ', 'insert ', 'alter ', 
                      'create ', 'truncate ', 'exec ', 'execute ', 'sp_', 'xp_', '--', '/*', '*/'];
    
    for (const keyword of dangerous) {
        if (sqlLower.includes(keyword)) {
            return {
                isValid: false,
                message: `❌ Dangerous keyword detected: ${keyword.trim()}`
            };
        }
    }
    
    // Check for multiple statements
    const cleaned = trimmed.replace(/;+$/, '');
    if (cleaned.includes(';')) {
        return {
            isValid: false,
            message: '❌ Multiple statements not allowed'
        };
    }
    
    return {
        isValid: true,
        message: '✓ Valid SELECT statement'
    };
}

function updateSQLValidation() {
    const editor = document.getElementById('sql-query-editor');
    const feedback = document.getElementById('sql-validation-feedback');
    const executeBtn = document.getElementById('execute-sql-btn');
    
    const sql = editor.value;
    const validation = validateSQL(sql);
    
    // Update state
    appState.sql.isValid = validation.isValid;
    appState.sql.validationMessage = validation.message;
    
    // Update UI
    editor.classList.remove('valid', 'invalid');
    feedback.className = 'validation-feedback';
    
    if (sql.trim()) {
        if (validation.isValid) {
            editor.classList.add('valid');
            feedback.classList.add('valid');
            feedback.textContent = validation.message;
            executeBtn.disabled = false;
        } else {
            editor.classList.add('invalid');
            feedback.classList.add('invalid');
            feedback.textContent = validation.message;
            executeBtn.disabled = true;
        }
    } else {
        feedback.textContent = '';
        executeBtn.disabled = true;
    }
}

// Mode switching
function switchMode(newMode) {
    const currentMode = appState.sql.mode;
    
    if (currentMode === newMode) return;
    
    // Check if SQL is edited in auto mode
    if (currentMode === 'auto' && appState.sql.isEdited) {
        const confirm = window.confirm(
            'You have edited the SQL. Switching to Manual mode will keep your changes. Continue?'
        );
        if (!confirm) return;
    }
    
    // Update state
    appState.sql.mode = newMode;
    
    // Update UI
    document.querySelectorAll('.mode-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.mode === newMode) {
            btn.classList.add('active');
        }
    });
    
    // Show/hide question input
    const questionContainer = document.getElementById('question-container');
    if (newMode === 'auto') {
        questionContainer.classList.remove('hidden');
        document.getElementById('submit-btn').textContent = 'Generate SQL';
    } else {
        questionContainer.classList.add('hidden');
    }
    
    // Update regenerate button visibility
    const regenerateBtn = document.getElementById('regenerate-btn');
    regenerateBtn.style.display = (newMode === 'auto' && appState.sql.isEdited) ? 'inline-block' : 'none';
    
    // Save state
    saveToSessionStorage();
    
    // Validate current SQL
    updateSQLValidation();
}

// SQL execution functions
async function generateSQL() {
    const question = document.getElementById('question-input').value;
    if (!question.trim()) {
        alert('Please enter a question.');
        return;
    }
    
    const editor = document.getElementById('sql-query-editor');
    const executeBtn = document.getElementById('execute-sql-btn');
    
    editor.value = 'Generating SQL...';
    executeBtn.disabled = true;
    
    // Reset analysis and visualization
    resetAnalysisState();
    resetVisualizationState();
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ question: question })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Store generated SQL
        appState.sql.query = data.sql_query;
        appState.sql.originalGenerated = data.sql_query;
        appState.sql.isEdited = false;
        
        // Update editor
        editor.value = data.sql_query;
        updateSQLValidation();
        
        // Handle results
        handleQuerySuccess(data, question);
        
    } catch (error) {
        console.error('Error generating SQL:', error);
        editor.value = '';
        alert(`Error generating SQL: ${error.message}`);
    }
}

async function executeManualSQL() {
    const sql = document.getElementById('sql-query-editor').value.trim();
    
    if (!sql) {
        alert('Please enter a SQL query.');
        return;
    }
    
    const validation = validateSQL(sql);
    if (!validation.isValid) {
        alert(`Invalid SQL: ${validation.message}`);
        return;
    }
    
    const executeBtn = document.getElementById('execute-sql-btn');
    const originalText = executeBtn.textContent;
    
    executeBtn.disabled = true;
    executeBtn.textContent = 'Executing...';
    
    // Reset analysis and visualization
    resetAnalysisState();
    resetVisualizationState();
    
    try {
        const response = await fetch('/api/execute-sql', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ sql: sql })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            executeBtn.textContent = originalText;
            executeBtn.disabled = false;
            return;
        }
        
        // Store successful query
        appState.sql.lastSuccessfulQuery = sql;
        
        // Handle results (no question for manual mode)
        handleQuerySuccess(data, null);
        
    } catch (error) {
        console.error('Error executing SQL:', error);
        alert(`Error executing SQL: ${error.message}`);
    } finally {
        executeBtn.textContent = originalText;
        executeBtn.disabled = false;
    }
}

// Helper functions
function formatSQL() {
    const editor = document.getElementById('sql-query-editor');
    let sql = editor.value;
    
    // Basic SQL formatting
    sql = sql.replace(/\s+/g, ' ').trim();
    sql = sql.replace(/\bSELECT\b/gi, 'SELECT\n  ');
    sql = sql.replace(/\bFROM\b/gi, '\nFROM\n  ');
    sql = sql.replace(/\bWHERE\b/gi, '\nWHERE\n  ');
    sql = sql.replace(/\bJOIN\b/gi, '\nJOIN\n  ');
    sql = sql.replace(/\bGROUP BY\b/gi, '\nGROUP BY\n  ');
    sql = sql.replace(/\bORDER BY\b/gi, '\nORDER BY\n  ');
    sql = sql.replace(/,/g, ',\n  ');
    
    editor.value = sql;
    appState.sql.query = sql;
    
    // Check if edited
    if (appState.sql.mode === 'auto' && sql !== appState.sql.originalGenerated) {
        appState.sql.isEdited = true;
        document.getElementById('sql-query-editor').classList.add('edited');
        document.getElementById('regenerate-btn').style.display = 'inline-block';
    }
    
    updateSQLValidation();
    saveToSessionStorage();
}

function clearSQL() {
    if (appState.sql.query && !confirm('Clear the SQL query?')) {
        return;
    }
    
    const editor = document.getElementById('sql-query-editor');
    editor.value = '';
    appState.sql.query = '';
    appState.sql.isEdited = false;
    editor.classList.remove('edited', 'valid', 'invalid');
    
    document.getElementById('regenerate-btn').style.display = 'none';
    updateSQLValidation();
    saveToSessionStorage();
}

function updateMetadataBar(data) {
    const metadataBar = document.getElementById('query-metadata-bar');
    const modeSpan = document.getElementById('metadata-mode');
    const questionSpan = document.getElementById('metadata-question');
    const timestampSpan = document.getElementById('metadata-timestamp');
    const rowcountSpan = document.getElementById('metadata-rowcount');
    
    // Mode
    const mode = data.question ? '🤖 AI Generated' : '✍️ Manual SQL';
    modeSpan.textContent = `Mode: ${mode}`;
    
    // Question (if available)
    if (data.question) {
        questionSpan.textContent = `Question: "${data.question}"`;
        questionSpan.style.display = 'flex';
    } else {
        questionSpan.style.display = 'none';
    }
    
    // Timestamp
    const now = new Date();
    timestampSpan.textContent = `Executed: ${now.toLocaleTimeString()}`;
    
    // Row count
    const rowCount = data.row_count || 0;
    const executionTime = data.execution_time_ms ? ` (${data.execution_time_ms.toFixed(0)}ms)` : '';
    rowcountSpan.textContent = `Rows: ${rowCount.toLocaleString()}${executionTime}`;
    
    metadataBar.style.display = 'flex';
}

function handleQuerySuccess(data, question) {
    // Store results in state
    appState.currentQuery.results = {
        columns: data.results.columns || [],
        rows: data.results.rows || []
    };
    appState.currentQuery.sql = data.sql_query;
    appState.currentQuery.question = question;
    appState.currentQuery.timestamp = Date.now();
    appState.currentQuery.executionMode = question ? 'auto' : 'manual';
    appState.currentQuery.rowCount = data.row_count || 0;
    appState.currentQuery.executionTimeMs = data.execution_time_ms || 0;
    
    // Display results in Results tab
    displayResults(data.results);
    
    // Update metadata bar
    updateMetadataBar(data);
    
    // Enable/disable Analysis tab based on dataset size
    const analysisTabBtn = document.getElementById('analysis-tab-btn');
    if (isAnalysisAvailable()) {
        analysisTabBtn.disabled = false;
        analysisTabBtn.title = '';
    } else {
        analysisTabBtn.disabled = true;
        analysisTabBtn.title = 'Analysis requires at least 2 rows';
    }
    
    // Enable visualizations tab
    const vizTabBtn = document.getElementById('visualizations-tab-btn');
    vizTabBtn.disabled = false;
    vizTabBtn.title = '';
    
    // Switch to Results tab
    switchTab('results');
}

function displayResults(results) {
    const resultsOutput = document.getElementById('results-output');
    
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

// ============================================
// DOM READY AND EVENT HANDLERS
// ============================================

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
            
            // Disable visualizations tab on error
            const vizTabBtn = document.getElementById('visualizations-tab-btn');
            vizTabBtn.disabled = true;
            vizTabBtn.title = 'No data available for visualization';
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
        
        // Reset visualization state for new query
        resetVisualizationState();
        
        // Enable visualizations tab (will check availability when clicked)
        const vizTabBtn = document.getElementById('visualizations-tab-btn');
        vizTabBtn.disabled = false;
        vizTabBtn.title = '';
        
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
    
    // Initialize visualization event listeners
    initializeVisualizationListeners();
    
    // ============================================
    // MANUAL SQL EDITING EVENT HANDLERS
    // ============================================
    
    // Restore state from sessionStorage
    restoreFromSessionStorage();
    
    // Mode switching event listeners
    document.getElementById('auto-mode-btn').addEventListener('click', () => {
        switchMode('auto');
    });
    
    document.getElementById('manual-mode-btn').addEventListener('click', () => {
        switchMode('manual');
    });
    
    // SQL Editor events
    const sqlEditor = document.getElementById('sql-query-editor');
    sqlEditor.addEventListener('input', () => {
        appState.sql.query = sqlEditor.value;
        
        // Check if edited in auto mode
        if (appState.sql.mode === 'auto' && sqlEditor.value !== appState.sql.originalGenerated) {
            appState.sql.isEdited = true;
            sqlEditor.classList.add('edited');
            document.getElementById('regenerate-btn').style.display = 'inline-block';
        } else if (appState.sql.mode === 'auto' && sqlEditor.value === appState.sql.originalGenerated) {
            appState.sql.isEdited = false;
            sqlEditor.classList.remove('edited');
            document.getElementById('regenerate-btn').style.display = 'none';
        }
        
        updateSQLValidation();
        saveToSessionStorage();
    });
    
    // Execute button - dual purpose (generate or execute)
    document.getElementById('execute-sql-btn').addEventListener('click', () => {
        if (appState.sql.mode === 'manual' || appState.sql.isEdited) {
            executeManualSQL();
        } else {
            // In auto mode with unedited SQL, just execute existing SQL
            if (appState.sql.query) {
                executeManualSQL();
            }
        }
    });
    
    // Generate SQL button (auto mode)
    document.getElementById('submit-btn').addEventListener('click', () => {
        generateSQL();
    });
    
    // Regenerate button
    document.getElementById('regenerate-btn').addEventListener('click', () => {
        if (confirm('Regenerate SQL? This will overwrite your edits.')) {
            generateSQL();
        }
    });
    
    // Format SQL button
    document.getElementById('format-sql-btn').addEventListener('click', () => {
        formatSQL();
    });
    
    // Clear SQL button
    document.getElementById('clear-sql-btn').addEventListener('click', () => {
        clearSQL();
    });
    
    // Keyboard shortcut: Ctrl+Enter to execute
    sqlEditor.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!document.getElementById('execute-sql-btn').disabled) {
                if (appState.sql.mode === 'manual' || appState.sql.isEdited) {
                    executeManualSQL();
                } else if (appState.sql.query) {
                    executeManualSQL();
                }
            }
        }
    });
    
    // Initialize UI based on restored state
    if (appState.sql.mode === 'manual') {
        switchMode('manual');
    }
    
    if (appState.sql.query) {
        sqlEditor.value = appState.sql.query;
        updateSQLValidation();
    }
});

// ============================================
// VISUALIZATION TAB LOGIC
// ============================================

function resetVisualizationState() {
    appState.visualization = {
        isAvailable: false,
        plotlyLoaded: appState.visualization.plotlyLoaded, // Keep plotly loaded status
        status: "idle",
        error: null,
        chartType: null,
        xColumn: null,
        yColumn: null,
        columnTypes: {},
        chartData: null,
        isSampled: false,
        originalRowCount: null,
        sampledRowCount: null
    };
}

function initializeVisualizationListeners() {
    // Chart type button listeners
    document.querySelectorAll('.chart-type-button').forEach(button => {
        button.addEventListener('click', () => {
            const chartType = button.dataset.chart;
            handleChartTypeSelection(chartType);
        });
    });
    
    // Chart type dropdown listener
    document.getElementById('chart-type-select').addEventListener('change', (e) => {
        handleChartTypeChange(e.target.value);
    });
    
    // Axis selector listeners
    document.getElementById('x-axis-select').addEventListener('change', handleAxisSelection);
    document.getElementById('y-axis-select').addEventListener('change', handleAxisSelection);
}

async function initializeVisualizationTab() {
    const results = appState.currentQuery.results;
    
    // Reset UI visibility
    document.getElementById('viz-unavailable').style.display = 'none';
    document.getElementById('chart-type-selector').style.display = 'none';
    document.getElementById('axis-config').style.display = 'none';
    document.getElementById('chart-container').style.display = 'none';
    document.getElementById('chart-error').style.display = 'none';
    document.getElementById('sampling-notice').style.display = 'none';
    
    // Check if visualization is available
    const availability = await checkVisualizationAvailability(results);
    
    if (!availability.available) {
        showVisualizationUnavailable(availability.reason);
        return;
    }
    
    // Store column types and mark as available
    appState.visualization.columnTypes = availability.column_types;
    appState.visualization.isAvailable = true;
    
    // Load Plotly if needed
    if (!appState.visualization.plotlyLoaded) {
        await loadPlotly();
    }
    
    // Show chart type selector or restore previous state
    if (appState.visualization.chartData) {
        // Restore previous chart
        document.getElementById('axis-config').style.display = 'flex';
        document.getElementById('chart-type-select').value = appState.visualization.chartType;
        populateAxisDropdowns(appState.visualization.chartType);
        document.getElementById('x-axis-select').value = appState.visualization.xColumn;
        if (appState.visualization.yColumn) {
            document.getElementById('y-axis-select').value = appState.visualization.yColumn;
        }
        renderChart(appState.visualization.chartData);
        if (appState.visualization.isSampled) {
            showSamplingNotice(appState.visualization.originalRowCount, appState.visualization.sampledRowCount);
        }
    } else {
        // Show chart type selector
        document.getElementById('chart-type-selector').style.display = 'flex';
    }
}

async function checkVisualizationAvailability(results) {
    if (!results || !results.rows || results.rows.length < 2) {
        return {
            available: false,
            reason: "At least 2 rows required for visualization."
        };
    }
    
    try {
        const response = await fetch('/api/check-visualization', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                columns: results.columns,
                rows: results.rows
            })
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error checking visualization availability:', error);
        return {
            available: false,
            reason: "Error checking visualization availability."
        };
    }
}

async function loadPlotly() {
    return new Promise((resolve, reject) => {
        if (appState.visualization.plotlyLoaded) {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'lib/plotly.min.js';
        script.onload = () => {
            appState.visualization.plotlyLoaded = true;
            resolve();
        };
        script.onerror = () => {
            reject(new Error('Failed to load Plotly.js library'));
        };
        document.head.appendChild(script);
    });
}

function handleChartTypeSelection(chartType) {
    appState.visualization.chartType = chartType;
    appState.visualization.xColumn = null;
    appState.visualization.yColumn = null;
    
    // Hide chart type selector, show axis config
    document.getElementById('chart-type-selector').style.display = 'none';
    document.getElementById('axis-config').style.display = 'flex';
    
    // Set dropdown value
    document.getElementById('chart-type-select').value = chartType;
    
    // Update axis labels and populate dropdowns
    updateAxisLabelsForChartType(chartType);
    populateAxisDropdowns(chartType);
}

function handleChartTypeChange(newChartType) {
    const oldChartType = appState.visualization.chartType;
    appState.visualization.chartType = newChartType;
    
    // Check if current selections are compatible
    const compatibility = {
        scatter: {x: ['numeric'], y: ['numeric']},
        bar: {x: ['categorical'], y: ['numeric']},
        line: {x: ['datetime', 'numeric'], y: ['numeric']},
        histogram: {x: ['numeric']}
    };
    
    const newReq = compatibility[newChartType];
    const xType = appState.visualization.xColumn ? appState.visualization.columnTypes[appState.visualization.xColumn] : null;
    const yType = appState.visualization.yColumn ? appState.visualization.columnTypes[appState.visualization.yColumn] : null;
    
    const xCompatible = xType && newReq.x.includes(xType);
    const yCompatible = !newReq.y || (yType && newReq.y.includes(yType));
    
    if (!xCompatible) appState.visualization.xColumn = null;
    if (!yCompatible) appState.visualization.yColumn = null;
    
    // Update UI
    updateAxisLabelsForChartType(newChartType);
    populateAxisDropdowns(newChartType);
    
    // Clear chart
    cleanupChart();
}

function updateAxisLabelsForChartType(chartType) {
    const labels = {
        scatter: {x: 'X-Axis (Numeric)', y: 'Y-Axis (Numeric)'},
        bar: {x: 'X-Axis (Categorical)', y: 'Y-Axis (Numeric)'},
        line: {x: 'X-Axis (Time/Numeric)', y: 'Y-Axis (Numeric)'},
        histogram: {x: 'Column (Numeric)', y: null}
    };
    
    document.getElementById('x-axis-label').textContent = labels[chartType].x;
    
    const yWrapper = document.getElementById('y-axis-wrapper');
    if (labels[chartType].y) {
        yWrapper.style.display = 'block';
        document.getElementById('y-axis-label').textContent = labels[chartType].y;
    } else {
        yWrapper.style.display = 'none';
    }
}

function populateAxisDropdowns(chartType) {
    const xSelect = document.getElementById('x-axis-select');
    const ySelect = document.getElementById('y-axis-select');
    
    // Clear and reset
    xSelect.innerHTML = '<option value="">Select Column</option>';
    ySelect.innerHTML = '<option value="">Select Column</option>';
    
    // Get compatible columns
    const compatibleX = getCompatibleColumns(chartType, 'x');
    const compatibleY = chartType !== 'histogram' ? getCompatibleColumns(chartType, 'y') : [];
    
    // Populate X-axis
    compatibleX.forEach(col => {
        const option = document.createElement('option');
        option.value = col;
        option.textContent = col;
        xSelect.appendChild(option);
    });
    
    // Populate Y-axis
    if (chartType !== 'histogram') {
        compatibleY.forEach(col => {
            const option = document.createElement('option');
            option.value = col;
            option.textContent = col;
            ySelect.appendChild(option);
        });
    }
}

function getCompatibleColumns(chartType, axis) {
    const compatibility = {
        scatter: {x: ['numeric'], y: ['numeric']},
        bar: {x: ['categorical'], y: ['numeric']},
        line: {x: ['datetime', 'numeric'], y: ['numeric']},
        histogram: {x: ['numeric']}
    };
    
    const allowedTypes = compatibility[chartType][axis];
    return Object.keys(appState.visualization.columnTypes).filter(col =>
        allowedTypes.includes(appState.visualization.columnTypes[col])
    );
}

let chartGenerationTimeout = null;

function handleAxisSelection() {
    const xColumn = document.getElementById('x-axis-select').value;
    const yColumn = document.getElementById('y-axis-select').value;
    const chartType = appState.visualization.chartType;
    
    appState.visualization.xColumn = xColumn || null;
    appState.visualization.yColumn = yColumn || null;
    
    clearTimeout(chartGenerationTimeout);
    
    const hasAllColumns = xColumn && (chartType === 'histogram' || yColumn);
    
    if (hasAllColumns) {
        chartGenerationTimeout = setTimeout(() => {
            generateChart();
        }, 300);
    }
}

async function generateChart() {
    const {chartType, xColumn, yColumn} = appState.visualization;
    const results = appState.currentQuery.results;
    
    appState.visualization.status = 'loading';
    
    // Show loading
    document.getElementById('chart-loading').style.display = 'block';
    document.getElementById('chart-container').style.display = 'none';
    document.getElementById('chart-error').style.display = 'none';
    document.getElementById('sampling-notice').style.display = 'none';
    
    try {
        let chartData;
        
        if (results.rows.length > 10000) {
            // Large dataset: use backend
            const response = await fetch('/api/visualize', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    columns: results.columns,
                    rows: results.rows,
                    chartType,
                    xColumn,
                    yColumn
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.message);
            }
            
            if (result.status === 'too_large') {
                throw new Error(result.message);
            }
            
            if (result.is_sampled) {
                appState.visualization.isSampled = true;
                appState.visualization.originalRowCount = result.original_row_count;
                appState.visualization.sampledRowCount = result.sampled_row_count;
                showSamplingNotice(result.original_row_count, result.sampled_row_count);
            }
            
            chartData = prepareChartDataClientSide({
                rows: result.data.rows,
                chartType,
                xColumn,
                yColumn
            });
        } else {
            // Small dataset: process client-side
            chartData = prepareChartDataClientSide({
                rows: results.rows,
                chartType,
                xColumn,
                yColumn
            });
        }
        
        await renderChart(chartData);
        appState.visualization.status = 'success';
        appState.visualization.chartData = chartData;
        
    } catch (error) {
        console.error('Chart generation error:', error);
        appState.visualization.status = 'error';
        appState.visualization.error = error.message;
        showChartError(error.message);
    } finally {
        document.getElementById('chart-loading').style.display = 'none';
    }
}

function prepareChartDataClientSide({rows, chartType, xColumn, yColumn}) {
    const plotlyData = [];
    const layout = {
        autosize: true,
        margin: {l: 60, r: 40, t: 60, b: 80}
    };
    const config = {responsive: true, displayModeBar: true};
    
    switch (chartType) {
        case 'scatter':
            plotlyData.push({
                x: rows.map(r => r[xColumn]),
                y: rows.map(r => r[yColumn]),
                mode: 'markers',
                type: 'scatter',
                marker: {size: 8, color: '#0066CC'}
            });
            layout.title = `${yColumn} vs ${xColumn}`;
            layout.xaxis = {title: xColumn};
            layout.yaxis = {title: yColumn};
            break;
            
        case 'bar':
            plotlyData.push({
                x: rows.map(r => r[xColumn]),
                y: rows.map(r => r[yColumn]),
                type: 'bar',
                marker: {color: '#0066CC'}
            });
            layout.title = `${yColumn} by ${xColumn}`;
            layout.xaxis = {title: xColumn};
            layout.yaxis = {title: yColumn};
            break;
            
        case 'line':
            plotlyData.push({
                x: rows.map(r => r[xColumn]),
                y: rows.map(r => r[yColumn]),
                type: 'scatter',
                mode: 'lines+markers',
                line: {color: '#0066CC'}
            });
            layout.title = `${yColumn} over ${xColumn}`;
            layout.xaxis = {title: xColumn};
            layout.yaxis = {title: yColumn};
            break;
            
        case 'histogram':
            plotlyData.push({
                x: rows.map(r => r[xColumn]),
                type: 'histogram',
                marker: {color: '#0066CC'}
            });
            layout.title = `Distribution of ${xColumn}`;
            layout.xaxis = {title: xColumn};
            layout.yaxis = {title: 'Frequency'};
            break;
    }
    
    return {data: plotlyData, layout, config};
}

async function renderChart(chartData) {
    cleanupChart();
    
    const container = document.getElementById('chart-container');
    container.style.display = 'block';
    
    await Plotly.newPlot(container, chartData.data, chartData.layout, chartData.config);
}

function cleanupChart() {
    const chartContainer = document.getElementById('chart-container');
    if (chartContainer && window.Plotly && chartContainer.data) {
        Plotly.purge(chartContainer);
        chartContainer.innerHTML = '';
    }
}

function showSamplingNotice(originalCount, sampledCount) {
    const notice = document.getElementById('sampling-notice');
    notice.textContent = `* Data sampled for performance. Displaying ${sampledCount.toLocaleString()} of ${originalCount.toLocaleString()} rows.`;
    notice.style.display = 'block';
}

function showChartError(message) {
    const errorDiv = document.getElementById('chart-error');
    errorDiv.textContent = `⚠️ ${message}`;
    errorDiv.style.display = 'block';
    document.getElementById('chart-container').style.display = 'none';
}

function showVisualizationUnavailable(reason) {
    document.getElementById('viz-unavailable').style.display = 'block';
    document.querySelector('#viz-unavailable .reason').textContent = reason;
    document.getElementById('chart-type-selector').style.display = 'none';
}
