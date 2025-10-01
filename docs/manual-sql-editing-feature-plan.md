# Manual SQL Editing Feature - Implementation Plan

**Author:** Business Analyst  
**Date:** January 10, 2025  
**Status:** Proposed  
**Priority:** User-Requested Enhancement

---

## Executive Summary

This document outlines the implementation plan for adding manual SQL editing capabilities to the SQL Chatbot application. The feature will allow users to:
- Write SQL queries manually from scratch
- Edit AI-generated SQL queries before execution
- Correct or refine SQL after reviewing AI suggestions

---

## Current System Analysis

### Existing Architecture

**Current Flow:**
1. User enters natural language question
2. Question sent to `/api/query` endpoint
3. Backend calls OpenAI API to generate SQL (`services.get_sql_from_gpt()`)
4. Generated SQL is automatically executed (`services.execute_sql_query()`)
5. Results returned and displayed with SQL shown in read-only format

**Key Components:**
- **Backend:** `app/main.py`, `app/services.py`
- **Frontend:** `static/index.html`, `static/app.js`, `static/styles.css`
- **Database:** SQL Server AdventureWorks2022
- **API:** OpenAI GPT for SQL generation

**Current Limitations:**
- SQL displayed in read-only `<pre>` tag
- No ability to edit generated SQL
- No way to write SQL manually
- Auto-execution prevents review before running
- No iterative refinement possible

---

## Proposed Solution

### Overview

Add a dual-mode system that supports both:
1. **Auto Mode (existing):** AI generates and executes SQL
2. **Manual Mode (new):** User writes/edits SQL before execution

### Key Design Principles

1. **Non-Breaking:** Maintain backward compatibility with existing workflow
2. **Progressive Enhancement:** Add new capabilities without removing old ones
3. **Security First:** Maintain existing SQL safety validation
4. **User Choice:** Allow users to choose their preferred workflow

---

## Implementation Plan

### Phase 1: Backend Changes

#### 1.1 New API Endpoint for Manual SQL Execution

**File:** `app/main.py`

**Add New Request Model:**
```python
class ExecuteSQLRequest(BaseModel):
    sql: str
```

**Add New Endpoint:**
```python
@app.post("/api/execute-sql")
async def execute_sql(request: ExecuteSQLRequest):
    """
    Execute user-provided SQL query with safety checks.
    
    Request body:
        sql: SQL query string to execute
        
    Returns:
        SQL query and results, or error message
    """
    try:
        # Validate SQL is safe
        if not services._is_safe_select(request.sql):
            return {
                "error": "Only SELECT statements are allowed. No data modification operations permitted.",
                "sql_query": request.sql,
                "results": {"columns": [], "rows": []}
            }
        
        # Execute the query
        results = services.execute_sql_query(request.sql)
        
        # Check for database errors
        if "error" in results:
            return {
                "error": results["error"],
                "sql_query": request.sql,
                "results": {"columns": [], "rows": []}
            }
        
        return {
            "sql_query": request.sql,
            "results": results
        }
    except Exception as e:
        logger.error(f"Manual SQL execution failed: {str(e)}", exc_info=True)
        return {
            "error": f"Execution failed: {str(e)}",
            "sql_query": request.sql,
            "results": {"columns": [], "rows": []}
        }
```

**Testing Checklist:**
- [ ] Endpoint accepts valid SELECT queries
- [ ] Endpoint rejects non-SELECT queries
- [ ] Endpoint rejects dangerous SQL patterns
- [ ] Error handling works correctly
- [ ] Response format matches existing `/api/query` endpoint

#### 1.2 Refactoring (Optional)

**Make safety validator publicly accessible:**
```python
# In services.py, consider making _is_safe_select public if needed by other modules
def is_safe_select(sql: str) -> bool:
    """Validate that SQL is a safe SELECT statement only."""
    # ... existing implementation ...
```

---

### Phase 2: Frontend UI Changes

#### 2.1 HTML Structure Updates

**File:** `static/index.html`

**Current Structure:**
```html
<textarea id="question-input" placeholder="Enter your question here..."></textarea>
<button id="submit-btn">Submit</button>
<hr>
<h2>Generated SQL Query:</h2>
<pre id="sql-query-output"></pre>
```

**Proposed New Structure:**
```html
<!-- Natural Language Input Section -->
<div class="query-input-section">
    <h2>Ask a Question or Write SQL</h2>
    
    <!-- Mode Selector -->
    <div class="mode-selector">
        <button id="auto-mode-btn" class="mode-btn active" data-mode="auto">
            🤖 AI Generate SQL
        </button>
        <button id="manual-mode-btn" class="mode-btn" data-mode="manual">
            ✍️ Write SQL Manually
        </button>
    </div>
    
    <!-- Natural Language Input (shown in auto mode) -->
    <div id="nl-input-container" class="input-container">
        <label for="question-input">Natural Language Question:</label>
        <textarea id="question-input" 
                  placeholder="Example: Show me the top 10 employees by salary"
                  rows="3"></textarea>
        <button id="generate-btn" class="primary-btn">Generate SQL</button>
    </div>
</div>

<hr>

<!-- SQL Editor Section -->
<div class="sql-editor-section">
    <div class="sql-editor-header">
        <h2>SQL Query:</h2>
        <div class="sql-editor-actions">
            <button id="format-sql-btn" class="secondary-btn" title="Format SQL">
                ⚡ Format
            </button>
            <button id="clear-sql-btn" class="secondary-btn" title="Clear SQL">
                🗑️ Clear
            </button>
        </div>
    </div>
    
    <!-- Editable SQL Textarea -->
    <textarea id="sql-editor" 
              class="sql-editor"
              placeholder="-- SQL query will appear here, or write your own SELECT statement"
              rows="8"
              spellcheck="false"></textarea>
    
    <!-- SQL Status Indicators -->
    <div id="sql-status" class="sql-status">
        <span id="sql-status-text"></span>
    </div>
    
    <!-- Execution Controls -->
    <div class="execution-controls">
        <button id="execute-sql-btn" class="primary-btn execute-btn" disabled>
            ▶️ Execute SQL
        </button>
        <button id="regenerate-sql-btn" class="secondary-btn" style="display: none;">
            🔄 Regenerate from Question
        </button>
    </div>
</div>

<!-- Rest of existing structure (tabs, results, etc.) -->
```

#### 2.2 CSS Updates

**File:** `static/styles.css`

**Add New Styles:**
```css
/* Mode Selector */
.mode-selector {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.mode-btn {
    flex: 1;
    padding: 12px 20px;
    border: 2px solid #ddd;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.mode-btn:hover {
    border-color: #0066CC;
    background: #f0f8ff;
}

.mode-btn.active {
    border-color: #0066CC;
    background: #0066CC;
    color: white;
}

/* SQL Editor */
.sql-editor-section {
    margin: 20px 0;
}

.sql-editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.sql-editor-actions {
    display: flex;
    gap: 8px;
}

.sql-editor {
    width: 100%;
    padding: 15px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-family: 'Courier New', Consolas, monospace;
    font-size: 14px;
    line-height: 1.6;
    resize: vertical;
    min-height: 150px;
    background: #f8f9fa;
    color: #333;
    transition: border-color 0.3s ease;
}

.sql-editor:focus {
    outline: none;
    border-color: #0066CC;
    background: white;
}

.sql-editor.edited {
    border-color: #ffc107;
    background: #fffef0;
}

.sql-editor.error {
    border-color: #dc3545;
    background: #fff5f5;
}

/* SQL Status */
.sql-status {
    margin: 10px 0;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 13px;
    min-height: 20px;
}

.sql-status.info {
    background: #d1ecf1;
    color: #0c5460;
}

.sql-status.warning {
    background: #fff3cd;
    color: #856404;
}

.sql-status.error {
    background: #f8d7da;
    color: #721c24;
}

/* Execution Controls */
.execution-controls {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}

.execute-btn {
    background: #28a745;
    padding: 12px 30px;
}

.execute-btn:hover:not(:disabled) {
    background: #218838;
}

.execute-btn:disabled {
    background: #6c757d;
    cursor: not-allowed;
    opacity: 0.6;
}

/* Button Styles */
.primary-btn {
    background: #0066CC;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.3s ease;
}

.primary-btn:hover:not(:disabled) {
    background: #0052a3;
}

.secondary-btn {
    background: white;
    color: #333;
    border: 2px solid #ddd;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
}

.secondary-btn:hover {
    border-color: #0066CC;
    color: #0066CC;
}

/* Input Container */
.input-container {
    margin-bottom: 20px;
}

.input-container label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #333;
}
```

---

### Phase 3: Frontend JavaScript Implementation

#### 3.1 State Management

**File:** `static/app.js`

**Add SQL State to appState:**
```javascript
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
    sql: {
        mode: "auto",           // "auto" | "manual"
        query: "",              // Current SQL in editor
        originalGenerated: "",  // Last AI-generated SQL
        isEdited: false,        // Has user modified the SQL?
        isValid: null,          // null | true | false
        validationMessage: ""
    },
    // ... existing state (analysis, visualization, ui) ...
};
```

#### 3.2 New Functions

**Mode Management:**
```javascript
function switchMode(newMode) {
    appState.sql.mode = newMode;
    
    // Update UI
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-mode="${newMode}"]`).classList.add('active');
    
    // Toggle visibility
    const nlContainer = document.getElementById('nl-input-container');
    const sqlEditor = document.getElementById('sql-editor');
    
    if (newMode === 'auto') {
        nlContainer.style.display = 'block';
        document.getElementById('regenerate-sql-btn').style.display = 'inline-block';
    } else {
        nlContainer.style.display = 'block'; // Keep visible but optional
        document.getElementById('regenerate-sql-btn').style.display = 'none';
    }
    
    // Focus appropriate input
    if (newMode === 'manual') {
        sqlEditor.focus();
    }
}
```

**SQL Validation:**
```javascript
function validateSQL(sql) {
    const trimmed = sql.trim().toLowerCase();
    
    if (!trimmed) {
        return { valid: false, message: "" };
    }
    
    // Basic client-side validation
    const isSelect = trimmed.startsWith('select') || trimmed.startsWith('with');
    if (!isSelect) {
        return { 
            valid: false, 
            message: "⚠️ Only SELECT statements are allowed"
        };
    }
    
    // Check for dangerous keywords
    const dangerous = ['drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate', 'exec'];
    for (const keyword of dangerous) {
        if (trimmed.includes(keyword)) {
            return { 
                valid: false, 
                message: `⚠️ Keyword '${keyword}' not allowed`
            };
        }
    }
    
    return { valid: true, message: "✓ Valid SELECT statement" };
}

function updateSQLValidation() {
    const sql = document.getElementById('sql-editor').value;
    const validation = validateSQL(sql);
    
    appState.sql.isValid = validation.valid;
    appState.sql.validationMessage = validation.message;
    
    // Update UI
    const statusDiv = document.getElementById('sql-status');
    const statusText = document.getElementById('sql-status-text');
    const executeBtn = document.getElementById('execute-sql-btn');
    
    statusText.textContent = validation.message;
    
    if (!sql.trim()) {
        statusDiv.className = 'sql-status';
        executeBtn.disabled = true;
    } else if (validation.valid) {
        statusDiv.className = 'sql-status info';
        executeBtn.disabled = false;
    } else {
        statusDiv.className = 'sql-status error';
        executeBtn.disabled = true;
    }
}
```

**SQL Execution:**
```javascript
async function executeManualSQL() {
    const sql = document.getElementById('sql-editor').value.trim();
    
    if (!sql) {
        alert('Please enter a SQL query.');
        return;
    }
    
    // Validate before sending
    const validation = validateSQL(sql);
    if (!validation.valid) {
        alert(validation.message);
        return;
    }
    
    // Show loading state
    const executeBtn = document.getElementById('execute-sql-btn');
    const originalText = executeBtn.textContent;
    executeBtn.disabled = true;
    executeBtn.textContent = '⏳ Executing...';
    
    // Clear previous results
    document.getElementById('results-output').innerHTML = '<p>Executing query...</p>';
    
    try {
        const response = await fetch('/api/execute-sql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sql: sql }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Handle response
        if (data.error) {
            handleQueryError(data.error, sql);
        } else {
            handleQuerySuccess(data, null); // No question in manual mode
        }
        
    } catch (error) {
        handleQueryError(error.message, sql);
    } finally {
        executeBtn.disabled = false;
        executeBtn.textContent = originalText;
    }
}
```

**Auto-Generation (Modified):**
```javascript
async function generateSQL() {
    const question = document.getElementById('question-input').value.trim();
    
    if (!question) {
        alert('Please enter a question.');
        return;
    }

    const sqlEditor = document.getElementById('sql-editor');
    sqlEditor.value = '-- Generating SQL...';
    
    // Reset state
    resetAnalysisState();
    resetVisualizationState();

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
        
        // Store generated SQL
        appState.sql.originalGenerated = data.sql_query;
        appState.sql.query = data.sql_query;
        appState.sql.isEdited = false;
        
        // Display SQL in editor
        sqlEditor.value = data.sql_query;
        
        // Handle success
        handleQuerySuccess(data, question);
        
        // Show regenerate button
        document.getElementById('regenerate-sql-btn').style.display = 'inline-block';
        
    } catch (error) {
        sqlEditor.value = '';
        handleQueryError(error.message, '');
    }
}
```

**Helper Functions:**
```javascript
function handleQueryError(errorMessage, sql) {
    document.getElementById('results-output').innerHTML = 
        `<p style="color: red;">Error: ${errorMessage}</p>`;
    
    // Disable tabs
    document.getElementById('analysis-tab-btn').disabled = true;
    document.getElementById('visualizations-tab-btn').disabled = true;
    
    console.error('Query error:', errorMessage);
}

function formatSQL() {
    const sqlEditor = document.getElementById('sql-editor');
    let sql = sqlEditor.value;
    
    // Simple SQL formatting (basic implementation)
    // For production, consider using a SQL formatting library
    sql = sql
        .replace(/\s+/g, ' ')
        .replace(/SELECT/gi, '\nSELECT')
        .replace(/FROM/gi, '\nFROM')
        .replace(/WHERE/gi, '\nWHERE')
        .replace(/JOIN/gi, '\nJOIN')
        .replace(/GROUP BY/gi, '\nGROUP BY')
        .replace(/ORDER BY/gi, '\nORDER BY')
        .trim();
    
    sqlEditor.value = sql;
    appState.sql.query = sql;
}

function clearSQL() {
    if (confirm('Clear the SQL editor?')) {
        document.getElementById('sql-editor').value = '';
        appState.sql.query = '';
        appState.sql.isEdited = false;
        updateSQLValidation();
    }
}
```

#### 3.3 Event Listeners

**Add to DOMContentLoaded:**
```javascript
document.addEventListener('DOMContentLoaded', () => {
    // ... existing initialization ...
    
    // Mode switching
    document.getElementById('auto-mode-btn').addEventListener('click', () => {
        switchMode('auto');
    });
    
    document.getElementById('manual-mode-btn').addEventListener('click', () => {
        switchMode('manual');
    });
    
    // SQL generation
    document.getElementById('generate-btn').addEventListener('click', generateSQL);
    
    // SQL execution
    document.getElementById('execute-sql-btn').addEventListener('click', executeManualSQL);
    
    // SQL regeneration
    document.getElementById('regenerate-sql-btn').addEventListener('click', async () => {
        if (appState.sql.isEdited) {
            if (!confirm('This will overwrite your edited SQL. Continue?')) {
                return;
            }
        }
        await generateSQL();
    });
    
    // SQL editor changes
    const sqlEditor = document.getElementById('sql-editor');
    sqlEditor.addEventListener('input', (e) => {
        appState.sql.query = e.target.value;
        appState.sql.isEdited = (e.target.value !== appState.sql.originalGenerated);
        
        // Update validation
        updateSQLValidation();
        
        // Visual indicator for edited SQL
        if (appState.sql.isEdited && appState.sql.originalGenerated) {
            sqlEditor.classList.add('edited');
        } else {
            sqlEditor.classList.remove('edited');
        }
    });
    
    // SQL formatting
    document.getElementById('format-sql-btn').addEventListener('click', formatSQL);
    
    // SQL clearing
    document.getElementById('clear-sql-btn').addEventListener('click', clearSQL);
    
    // Keyboard shortcuts
    sqlEditor.addEventListener('keydown', (e) => {
        // Ctrl+Enter to execute
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            if (!document.getElementById('execute-sql-btn').disabled) {
                executeManualSQL();
            }
        }
    });
});
```

---

### Phase 4: Testing & Validation

#### 4.1 Unit Testing Checklist

**Backend Tests:**
- [ ] `/api/execute-sql` accepts valid SELECT queries
- [ ] `/api/execute-sql` rejects INSERT/UPDATE/DELETE queries
- [ ] `/api/execute-sql` rejects SQL injection attempts
- [ ] `/api/execute-sql` handles database connection errors
- [ ] `/api/execute-sql` handles malformed SQL syntax
- [ ] Error messages are user-friendly

**Frontend Tests:**
- [ ] Mode switching works correctly
- [ ] SQL editor accepts input
- [ ] SQL validation provides accurate feedback
- [ ] Execute button enables/disables appropriately
- [ ] Auto-generate workflow still works
- [ ] Manual execution workflow works
- [ ] Edit-then-execute workflow works
- [ ] Regenerate overwrites edited SQL (with confirmation)
- [ ] Clear SQL works
- [ ] Format SQL works (basic)
- [ ] Keyboard shortcuts work (Ctrl+Enter)

#### 4.2 Integration Testing

**Workflows to Test:**
1. **Pure Auto Mode:**
   - Enter question → Generate → Auto-display results
   
2. **Auto with Edit:**
   - Enter question → Generate → Edit SQL → Execute → View results
   
3. **Pure Manual Mode:**
   - Switch to manual → Write SQL → Execute → View results
   
4. **Iterative Refinement:**
   - Generate → Execute → Edit → Execute → Repeat

**Cross-Feature Integration:**
- [ ] Analysis tab works with manually executed queries
- [ ] Visualization tab works with manually executed queries
- [ ] Error states handled gracefully
- [ ] State persistence across tab switches

#### 4.3 User Acceptance Testing

**Test Scenarios:**
1. Beginner user generates SQL and views results (existing workflow)
2. Intermediate user generates SQL, edits minor typo, executes
3. Advanced user writes complex SQL from scratch
4. User generates SQL, doesn't like it, regenerates
5. User switches between auto and manual modes
6. User tries to execute dangerous SQL (should be blocked)

---

### Phase 5: Documentation & Deployment

#### 5.1 User Documentation

**Create:** `USER_GUIDE_SQL_EDITING.md`

**Contents:**
- How to use Auto mode (AI generation)
- How to use Manual mode (write from scratch)
- How to edit generated SQL
- Keyboard shortcuts
- Safety limitations
- Troubleshooting common issues

#### 5.2 Developer Documentation

**Update:** `README.md`

**Add Section:**
```markdown
## Manual SQL Editing

The application supports two modes for SQL queries:

### Auto Mode (AI-Generated)
1. Enter natural language question
2. Click "Generate SQL"
3. Review generated SQL
4. Optionally edit before execution
5. Click "Execute SQL"

### Manual Mode
1. Switch to "Write SQL Manually"
2. Write SQL directly in editor
3. Click "Execute SQL"

### API Endpoints
- `POST /api/query` - Generate and execute SQL from natural language
- `POST /api/execute-sql` - Execute user-provided SQL
```

#### 5.3 Deployment Steps

1. **Pre-Deployment:**
   - [ ] Complete all testing
   - [ ] Code review
   - [ ] Update documentation
   - [ ] Backup current production code

2. **Deployment:**
   - [ ] Deploy backend changes
   - [ ] Deploy frontend changes
   - [ ] Update environment configuration if needed
   - [ ] Verify deployment in staging

3. **Post-Deployment:**
   - [ ] Monitor error logs
   - [ ] Collect user feedback
   - [ ] Track usage metrics (auto vs manual mode)
   - [ ] Address any critical issues

---

## Security Considerations

### Current Safety Measures (Maintained)

✅ **Already Implemented:**
- SQL injection protection via `_is_safe_select()`
- Only SELECT statements allowed
- No data modification operations (INSERT, UPDATE, DELETE)
- No schema changes (CREATE, ALTER, DROP)
- No stored procedures execution
- No comment injection
- No multiple statement execution

### Additional Security Recommendations

1. **Rate Limiting:**
   - Implement rate limiting on `/api/execute-sql` endpoint
   - Limit to 60 requests per minute per user/IP
   - Prevents abuse and DOS attacks

2. **Query Complexity Limits:**
   - Add timeout for long-running queries (e.g., 30 seconds)
   - Limit result set size (already implemented via TOP 200)
   - Consider memory usage limits for large results

3. **Audit Logging:**
   ```python
   # Log all manual SQL executions
   logger.info(f"Manual SQL execution: {sql[:100]}... by user {user_id}")
   ```

4. **User Confirmation for Potential Issues:**
   - Warn if query doesn't have WHERE clause (full table scan)
   - Warn if query returns > 10,000 rows
   - Confirm before executing complex joins

5. **Content Security Policy:**
   - Ensure CSP headers prevent XSS attacks
   - Sanitize all user input (already done via parametrized queries)

---

## Future Enhancements

### Phase 6: Advanced Features (Future)

#### 6.1 SQL History
- Store last 10 queries in localStorage
- Quick access dropdown for recent queries
- Save favorite queries
- Export query history

#### 6.2 SQL Syntax Highlighting
- Integrate CodeMirror or Monaco Editor
- Syntax highlighting for SQL keywords
- Auto-completion for table/column names
- Line numbers and bracket matching

#### 6.3 Query Templates
- Pre-built query templates for common scenarios
- Template library (top N, aggregations, joins, etc.)
- User-defined templates

#### 6.4 SQL Explain Plan
- Add "Explain Plan" button
- Show execution plan before running
- Identify performance bottlenecks
- Suggest optimizations

#### 6.5 Multi-Query Support
- Allow multiple queries separated by semicolons
- Execute queries sequentially
- Display results in separate tabs

#### 6.6 Query Sharing
- Generate shareable links for queries
- Export queries as SQL files
- Import SQL files

---

## Metrics & Success Criteria

### Key Performance Indicators

1. **Usage Metrics:**
   - % of queries using auto mode vs manual mode
   - % of generated queries that get edited
   - Average time to execute query
   - Number of regeneration requests

2. **Quality Metrics:**
   - Error rate for manually entered queries
   - Error rate for AI-generated queries
   - Query execution success rate
   - Average query complexity

3. **User Satisfaction:**
   - User feedback/ratings
   - Feature adoption rate
   - Support ticket volume
   - Time saved vs pure manual SQL writing

### Success Criteria

✅ **MVP Success:**
- Users can write SQL manually
- Users can edit generated SQL
- No breaking changes to existing workflows
- 95%+ query success rate maintained

✅ **Full Success:**
- 30%+ of users utilize manual editing
- < 5% increase in error rates
- Positive user feedback (4+ stars)
- Reduced support requests for "how to modify SQL"

---

## Timeline Estimate

### Phase 1: Backend (0.5 day)
- [ ] Implement `/api/execute-sql` endpoint - 2 hours
- [ ] Add request validation - 1 hour
- [ ] Add error handling - 1 hour
- [ ] Testing - 2 hours

### Phase 2: Frontend HTML/CSS (0.5 day)
- [ ] Update HTML structure - 2 hours
- [ ] Add new CSS styles - 1 hour
- [ ] Responsive design adjustments - 1 hour

### Phase 3: Frontend JavaScript (1 day)
- [ ] State management updates - 2 hours
- [ ] Mode switching logic - 1 hour
- [ ] SQL validation - 1 hour
- [ ] Event handlers - 2 hours
- [ ] Integration with existing code - 2 hours

### Phase 4: Testing (1 day)
- [ ] Unit testing - 2 hours
- [ ] Integration testing - 2 hours
- [ ] User acceptance testing - 2 hours
- [ ] Bug fixes - 2 hours

### Phase 5: Documentation & Deployment (0.5 day)
- [ ] User documentation - 1 hour
- [ ] Developer documentation - 1 hour
- [ ] Deployment - 2 hours

**Total Estimated Time: 3.5 days**

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking existing auto-generation workflow | High | Low | Thorough testing, maintain backward compatibility |
| Users write dangerous SQL | High | Medium | Strict validation, clear error messages |
| Performance degradation | Medium | Low | Query timeout limits, result set limits |
| User confusion with two modes | Medium | Medium | Clear UI, good defaults, documentation |
| Increased support burden | Low | Medium | Comprehensive help text, intuitive UI |

---

## Conclusion

This implementation plan provides a comprehensive roadmap for adding manual SQL editing capabilities to the SQL Chatbot application. The proposed solution:

- ✅ Maintains backward compatibility
- ✅ Adds powerful new capabilities for advanced users
- ✅ Maintains security through strict validation
- ✅ Provides clear migration path with minimal risk
- ✅ Can be implemented in estimated 3.5 days

The feature empowers users to:
- Learn from AI-generated SQL
- Refine queries for specific needs
- Write complex queries not easily described in natural language
- Iterate quickly without starting from scratch

**Next Step:** Review this plan with stakeholders and proceed with implementation approval.

---

## Appendix A: API Examples

### Generate SQL (Existing)
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me top 10 employees"}'
```

Response:
```json
{
  "sql_query": "SELECT TOP 10 * FROM HumanResources.Employee",
  "results": {
    "columns": ["BusinessEntityID", "JobTitle", ...],
    "rows": [...]
  }
}
```

### Execute Manual SQL (New)
```bash
curl -X POST http://localhost:8000/api/execute-sql \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT TOP 5 FirstName, LastName FROM Person.Person"}'
```

Response:
```json
{
  "sql_query": "SELECT TOP 5 FirstName
