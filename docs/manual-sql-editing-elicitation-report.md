# Manual SQL Editing Feature - Elicitation Report

**Project:** SQL Chatbot V2  
**Feature:** Manual SQL Editing Capability  
**Business Analyst:** Mary (Interactive Elicitation Session)  
**Date:** January 10, 2025  
**Session Type:** Advanced Elicitation & Gap Analysis  
**Deployment Context:** Local Development, Single Specialist User

---

## Executive Summary

This report documents the comprehensive elicitation findings and approved solutions for implementing manual SQL editing capabilities in the SQL Chatbot application. Through interactive analysis, we identified and resolved ambiguities across four critical categories: User Experience, Technical Implementation, Security, and Integration. All solutions have been tailored for a local development environment with a specialist user who requires minimal friction and maximum flexibility.

### Key Decisions Made

- **Validation Approach:** Backend-only validation, zero frontend validation (simplified per user request)
- **Security Model:** Localhost-only binding, no authentication (local dev setup)
- **Result Limits:** No enforcement - trust specialist user judgment
- **Integration Strategy:** Analysis/Visualization tabs work for both auto and manual queries
- **User Experience:** Dual-mode system with SQL preservation across mode switches

---

## Category 1: User Experience & Workflow Clarity

### Findings & Approved Solutions

#### 1.1 Mode Transition Behavior ✅

**Finding:** Unclear what happens to SQL when users switch between Auto and Manual modes.

**Approved Solution:**
- **Preserve SQL across all mode switches** - never destroy user work
- Show confirmation only when switching from Manual→Auto with unsaved SQL
- SQL in editor persists during mode transitions
- No data loss warnings needed for other transitions

**Implementation:**
```javascript
function switchMode(newMode) {
    const currentSQL = appState.sql.query.trim();
    const hasUnsavedSQL = currentSQL.length > 0;
    
    if (appState.sql.mode === 'manual' && newMode === 'auto' && hasUnsavedSQL) {
        if (!confirm('Switching to Auto mode will keep your SQL. Generate new SQL to replace it. Continue?')) {
            return;
        }
    }
    
    appState.sql.mode = newMode;
    // SQL persists
}
```

---

#### 1.2 Default State & First-Time User Experience ✅

**Finding:** Not clear what users see on first load.

**Approved Solution:**
- **Default Mode:** Auto mode (maintains current user behavior)
- **SQL Editor:** Empty with helpful placeholder text
- **Placeholder:** `"-- SQL query will appear here after generation\n-- Or switch to Manual mode to write your own SELECT statement"`
- **State Persistence:** Use sessionStorage (clears on browser close, persists on refresh)
- **First-Time Help:** Brief tooltip/banner introducing dual-mode system (show once via localStorage flag)

**Implementation:**
```javascript
// On page load
const lastMode = sessionStorage.getItem('sql_mode') || 'auto';
const lastSQL = sessionStorage.getItem('last_sql') || '';
appState.sql.mode = lastMode;

if (lastSQL) {
    document.getElementById('sql-editor').value = lastSQL;
}

if (!localStorage.getItem('sql_editing_introduced')) {
    showWelcomeTooltip();
    localStorage.setItem('sql_editing_introduced', 'true');
}
```

---

#### 1.3 Generate vs Execute Button Workflow ✅

**Finding:** Two-button workflow might cause confusion.

**Approved Solution:**
- **Two-Button Approach:**
  - "Generate SQL" button (Auto mode) - Generates SQL, loads into editor, does NOT execute
  - "Execute SQL" button (Both modes) - Executes whatever is in the editor
- **Optional Enhancement:** Add checkbox "☑ Auto-execute after generation" (default OFF for safety)

**Rationale:** Specialist users benefit from review-before-execute workflow. Two buttons provide clear separation of concerns.

---

#### 1.4 AI Generation Feedback ✅

**Finding:** Insufficient feedback during SQL generation.

**Approved Solution:**
- **Multi-stage visual feedback:**
  - Stage 1: Immediate "Generating..." indicator in button and editor placeholder
  - Stage 2: After 3 seconds, show "Still working..." message
  - Timeout: 30-second limit with AbortSignal
  - Cancel Button: Show during generation, uses AbortController
  
**Implementation:**
```javascript
async function generateSQL() {
    sqlEditor.placeholder = '⏳ Calling AI to generate SQL...';
    generateBtn.textContent = '⏳ Generating...';
    
    const progressTimeout = setTimeout(() => {
        sqlEditor.placeholder = '⏳ Still working... (Complex question may take longer)';
    }, 3000);
    
    try {
        const response = await fetch('/api/query', {
            signal: AbortSignal.timeout(30000)
        });
        // Handle response...
    } catch (error) {
        if (error.name === 'TimeoutError') {
            sqlEditor.value = '-- Generation timed out after 30 seconds';
        }
    } finally {
        clearTimeout(progressTimeout);
        // Restore UI...
    }
}
```

---

## Category 2: Technical Implementation Details

### Findings & Approved Solutions

#### 2.1 Database Connection Pooling & Rate Limiting ✅

**Finding:** Manual execution might overwhelm database connections.

**Approved Solution:**
- **Rate Limiting:** 30 requests/minute per IP for `/api/execute-sql`
- **Library:** Use `slowapi` for FastAPI
- **Connection Pooling:** Rely on existing pyodbc/SQLAlchemy pooling (no changes needed)
- **Timeout:** 30-second query timeout enforced

**Implementation:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/execute-sql")
@limiter.limit("30/minute")
async def execute_sql(request: Request, sql_request: ExecuteSQLRequest):
    # Implementation...
```

---

#### 2.2 Response Format Consistency ✅

**Finding:** Need standardized response schema across both endpoints.

**Approved Solution:**
- **Unified Schema:** Both `/api/query` and `/api/execute-sql` return identical structure
- **Schema Fields:**
  - `sql_query`: string
  - `question`: Optional[string] (null for manual execution)
  - `results`: {columns: [], rows: []}
  - `execution_time_ms`: float
  - `row_count`: int
  - `error`: Optional[string]

**Implementation:**
```python
class QueryResponse(BaseModel):
    sql_query: str
    question: Optional[str] = None
    results: QueryResults
    execution_time_ms: Optional[float] = None
    row_count: int
    error: Optional[str] = None

@app.post("/api/query", response_model=QueryResponse)
@app.post("/api/execute-sql", response_model=QueryResponse)
```

---

#### 2.3 SQL Validation Logic ⚠️ SIMPLIFIED PER USER REQUEST ✅

**Finding:** Frontend and backend validation could diverge.

**Approved Solution:**
- **Backend-Only Validation** - Single source of truth
- **Zero Frontend Validation** - No IntelliSense, no client-side checks
- **Execute button** - Enabled whenever SQL textarea has content
- **Simple and Fast** - No complexity, no sync issues

**Rationale:** User specifically requested simple approach without frontend validation. Acceptable tradeoff: every invalid query makes round trip to server, but implementation is much simpler.

**Implementation:**
```javascript
// FRONTEND: Simple enable/disable only
sqlEditor.addEventListener('input', (e) => {
    executeBtn.disabled = e.target.value.trim().length === 0;
    // No validation - trust backend
});

// BACKEND: Single validation point
@app.post("/api/execute-sql")
async def execute_sql(request: ExecuteSQLRequest):
    if not services._is_safe_select(request.sql):
        return QueryResponse(
            error="Only SELECT statements are allowed",
            error_code="VALIDATION_FAILED"
        )
```

---

#### 2.4 Error Response Structure ✅

**Finding:** Need consistent error handling across endpoints.

**Approved Solution:**
- **Typed Error Codes:**
  - `VALIDATION_FAILED` - Client-side error (invalid SQL)
  - `DB_ERROR` - Database execution error
  - `TIMEOUT` - Query exceeded 30 seconds
  - `INTERNAL_ERROR` - Server error
  
- **Error Response:**
  ```json
  {
    "error": "user-friendly message",
    "error_code": "VALIDATION_FAILED",
    "error_type": "client",
    "sql_query": "...",
    "results": {"columns": [], "rows": []}
  }
  ```

---

#### 2.5 Logging & Monitoring ✅

**Finding:** Need logging without exposing sensitive data.

**Approved Solution:**
- **Sanitized Logging:** Replace string literals and numbers in SQL before logging
- **Query Hash:** Track same query across executions
- **Log Fields:** IP, hash, sanitized SQL, execution time, row count, success/failure

**Implementation:**
```python
def sanitize_sql_for_logging(sql: str, max_length: int = 100) -> str:
    sanitized = re.sub(r"'[^']*'", "'<STRING>'", sql)
    sanitized = re.sub(r'\b\d{9,}\b', '<NUMBER>', sanitized)
    return sanitized[:max_length] + ("..." if len(sanitized) > max_length else "")

def get_sql_hash(sql: str) -> str:
    return hashlib.sha256(sql.encode()).hexdigest()[:16]

# Log example:
logger.info(f"MANUAL_SQL_START | IP: {client_ip} | HASH: {sql_hash} | SQL: {sql_sanitized}")
```

---

#### 2.6 Frontend State Management ✅

**Finding:** State transitions not fully specified.

**Approved Solution:**
- **State Object:** Track mode, query, originalGenerated, isEdited, timestamps
- **Transition Rules:**
  - On generate: Store as originalGenerated, isEdited=false
  - On edit: Set isEdited=true if differs from originalGenerated
  - On execute: Store as lastSuccessfulQuery
  - On mode switch: Preserve all SQL
  - On regenerate: Confirm if edited, then overwrite
  
- **Persistence:** Save to sessionStorage on every change
- **Multi-Tab:** Accept independent state per tab (simpler than cross-tab sync)

**Implementation:**
```javascript
const appState = {
    sql: {
        mode: "auto",
        query: "",
        originalGenerated: "",
        lastSuccessfulQuery: "",
        isEdited: false,
        lastExecutionTime: null
    }
};

function saveToSessionStorage() {
    sessionStorage.setItem('sql_state', JSON.stringify(appState.sql));
}
```

---

## Category 3: Security & Validation Concerns

### Deployment Context: Local Development Only ✅

**User Specification:** Local development setup, single specialist user, localhost-only access.

### Findings & Approved Solutions

#### 3.1 Authentication & Authorization ✅

**Finding:** No auth layer specified.

**Approved Solution: Option A - Local Development Only (Minimal Security)**
- **No Authentication** - Not needed for localhost-only deployment
- **Host Binding:** Restrict to `127.0.0.1` only
- **Firewall Protection:** Rely on OS-level firewall

**Implementation:**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)  # localhost only
```

**Future Options:**
- Option B: API Key authentication for internal network sharing
- Option C: Full OAuth/JWT for production deployment

---

#### 3.2 Data Exposure & Privacy ✅

**Finding:** No table-level restrictions specified.

**Approved Solution: NO RESTRICTIONS**
- **Database:** AdventureWorks2022 is Microsoft sample database with fictional data
- **Access Level:** Full query access for specialist user
- **Rationale:** No real PII or sensitive data in sample database
- **Optional Enhancement:** Warning system for large tables (non-blocking)

**For Future Production Use:**
- Create read-only database user
- Grant SELECT permissions on approved schemas only
- Document sensitive tables
- Use database-level security (simpler than application-level)

---

#### 3.3 Logging Privacy ✅

**Finding:** Logs might expose sensitive query values.

**Approved Solution: Sanitized Logging**
- Replace string literals with `<STRING>` placeholder
- Replace long numbers with `<NUMBER>` placeholder
- Include query hash for tracking
- Log structure visible, values protected
- First 100 characters only

**Example Log Output:**
```
2025-01-10 14:30:15 - MANUAL_SQL_START | IP: 127.0.0.1 | HASH: a3f2b8c1 | SQL: SELECT FirstName, LastName FROM Person.Person WHERE BusinessEntityID = <NUMBER>
2025-01-10 14:30:15 - MANUAL_SQL_SUCCESS | HASH: a3f2b8c1 | TIME_MS: 45.23 | ROWS: 1
```

---

#### 3.4 CORS & API Security Headers ✅

**Approved Solution:**
- **CORS Origins:** Restrict to `http://localhost:8000` and `http://127.0.0.1:8000`
- **Security Headers:** X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy
- **Methods:** Allow GET and POST only

**Implementation:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)
```

---

#### 3.5 Query Timeout ✅

**Approved Solution:**
- **Timeout:** 30 seconds per query
- **Implementation:** `asyncio.wait_for()` with timeout parameter
- **Error Response:** Clear timeout message with error code `TIMEOUT`

---

#### 3.6 Result Size Limits ⚠️ NOT ENFORCED PER USER REQUEST ✅

**Finding:** Plan mentioned TOP 200 limit.

**User Decision:** **No result limits** - Trust specialist user to manage query scope themselves.

**Rationale:** Specialist users know what they're doing, don't artificially restrict their capabilities.

---

## Category 4: Integration with Existing Features

### Findings & Approved Solutions

#### 4.1 Analysis Tab Integration ✅

**Finding:** Analysis service needs original question - not available for manual queries.

**Approved Solution: Pragmatic Hybrid**
- **Analysis works for both modes**
- **With Question (Auto mode):** Full context, better analysis quality
- **Without Question (Manual mode):** SQL + results only, slightly degraded quality
- **Visual Indicator:** Show `*` symbol on Analysis tab when in SQL-only mode
- **Backend Change:** Make `question` parameter optional in `/api/analyze`

**Implementation:**
```python
class AnalyzeRequest(BaseModel):
    sql_query: str
    results: QueryResults
    question: Optional[str] = None

@app.post("/api/analyze")
async def analyze_query(request: AnalyzeRequest):
    if request.question:
        # Full context analysis
        prompt = f"User Question: {request.question}\nSQL: {request.sql_query}\n..."
    else:
        # SQL-only analysis
        prompt = f"SQL: {request.sql_query}\nDescribe what data this retrieves..."
```

**User Experience:**
- ✅ No functionality loss
- ✅ Analysis available for all queries
- ✅ Clear visual indicator of mode
- ✅ Quality difference acceptable

---

#### 4.2 Visualization Tab Integration ✅

**Finding:** Does visualization need question context?

**Approved Solution: NO CHANGES NEEDED**
- **Visualization is question-agnostic** - already works!
- **Chart recommendations** based on column types and data patterns, not user intent
- **Logic:** Numeric columns → line/bar/scatter, Categorical + Numeric → pie/grouped bar, etc.
- **Compatibility:** Works identically for auto and manual queries

**Conclusion:** Visualization service already compatible with manual SQL execution.

---

#### 4.3 Tab State Management ✅

**Finding:** Risk of stale analysis/visualization after query changes.

**Approved Solution: Hash Tracking with Auto-Clear**
- **Query Hash:** Generate hash from SQL to track which query tabs are analyzing
- **Auto-Clear:** Reset Analysis and Visualization tabs when new query executes
- **Stale Indicator:** Visual warning if tabs show data for previous query
- **Auto-Refresh:** When switching to stale tab, automatically request fresh analysis/visualization

**Implementation:**
```javascript
function getQueryHash(sql) {
    return btoa(sql).substring(0, 16);
}

async function executeSQL(sql, question = null) {
    resetAnalysisState();
    resetVisualizationState();
    
    appState.currentQuery = {
        sql: sql,
        question: question,
        hash: getQueryHash(sql),
        timestamp: Date.now()
    };
    
    updateTabStates();
}

// CSS for stale indicator
.tab-btn.stale {
    background: #fff3cd;
    border-color: #ffc107;
}
.tab-btn.stale::after {
    content: " ⚠️";
}
```

---

#### 4.4 Results Display Consistency ✅

**Approved Solution: Metadata Bar**
- **Query Metadata Bar** shows:
  - Mode: 🤖 AI Generated or ✍️ Manual
  - Question: (shown only if available)
  - Execution Time: "Just now", "5 min ago", etc.
  - Row Count: Formatted with commas
  
**Implementation:**
```html
<div class="query-metadata">
    <div class="metadata-item">
        <strong>Mode:</strong> 
        <span id="query-mode-display">AI Generated</span>
    </div>
    <div class="metadata-item" id="query-question-display">
        <strong>Question:</strong> 
        <span id="query-question-text"></span>
    </div>
    <div class="metadata-item">
        <strong>Executed:</strong> 
        <span id="query-timestamp">Just now</span>
    </div>
    <div class="metadata-item">
        <strong>Rows:</strong> 
        <span id="query-row-count">0</span>
    </div>
</div>
```

---

#### 4.5 Code Impact Assessment ✅

**Files Requiring Modification:**

**High Impact (Major Changes):**
- `static/app.js` - State management, mode switching, execution flow
- `static/index.html` - Mode selector, SQL editor, execution controls
- `static/styles.css` - New UI components styling

**Medium Impact (New Endpoints/Models):**
- `app/main.py` - New `/api/execute-sql` endpoint, ExecuteSQLRequest model

**Low Impact (Parameter Changes):**
- `app/analysis_service.py` or relevant file - Make question optional in AnalyzeRequest

**Functions Requiring Updates:**
```
DOMContentLoaded event handler (major refactor)
handleQuerySuccess(data, question) (add mode awareness)
requestAnalysis() (handle optional question)
resetAnalysisState() (add hash tracking)
resetVisualizationState() (add hash tracking)

New Functions:
+ switchMode(newMode)
+ executeManualSQL()
+ generateSQL()
+ formatSQL()
+ clearSQL()
+ updateTabStates()
+ getQueryHash()
```

---

#### 4.6 Feature Flag ✅

**Approved Solution: localStorage Toggle**
- **Default:** Feature ON
- **Toggle:** `localStorage.setItem('feature_manual_sql', 'false')` to disable
- **Behavior when OFF:** Hide manual mode button, make SQL editor read-only
- **Purpose:** Easy rollback if issues arise, no code changes needed

**Optional Enhancement:** Server-side environment variable for production deployments.

---

## Implementation Recommendations

### Phase 1: Backend (Priority: High)

**Estimated Time: 4 hours**

1. **Add New Endpoint** (1 hour)
   ```python
   @app.post("/api/execute-sql")
   async def execute_sql(request: ExecuteSQLRequest):
       # Validation, execution, logging
   ```

2. **Standardize Response Models** (1 hour)
   - Create `QueryResponse` Pydantic model
   - Apply to both `/api/query` and `/api/execute-sql`
   - Ensure consistent error handling

3. **Update Analysis Endpoint** (1 hour)
   - Make `question` optional in `AnalyzeRequest`
   - Modify analysis prompt generation logic
   - Test with and without question context

4. **Add Logging & Monitoring** (1 hour)
   - Implement sanitized SQL logging
   - Add query hash generation
   - Configure log formatting

**Testing:**
- Validate endpoint accepts valid SELECT queries
- Validate endpoint rejects non-SELECT queries
- Test error response consistency
- Test timeout behavior
- Verify logging output format

---

### Phase 2: Frontend HTML/CSS (Priority: High)

**Estimated Time: 3 hours**

1. **HTML Structure Updates** (1.5 hours)
   - Add mode selector buttons
   - Replace `<pre>` with `<textarea id="sql-editor">`
   - Add execution controls section
   - Add query metadata display bar

2. **CSS Styling** (1.5 hours)
   - Mode selector styles
   - SQL editor styles (focus states, edited indicator)
   - Execution controls layout
   - Query metadata bar
   - Stale tab indicators
   - Responsive design adjustments

**Testing:**
- Verify responsive layout on different screen sizes
- Test focus states and visual feedback
- Ensure accessibility (keyboard navigation)

---

### Phase 3: Frontend JavaScript (Priority: High)

**Estimated Time: 8 hours**

1. **State Management** (2 hours)
   - Extend `appState` object with SQL substruct
   - Implement sessionStorage persistence
   - Add hash tracking for query identity

2. **Mode Switching Logic** (1 hour)
   - Implement `switchMode()` function
   - Handle SQL preservation
   - Update UI visibility

3. **Query Execution Flow** (2 hours)
   - Split current flow into `generateSQL()` and `executeManualSQL()`
   - Implement separate execution for manual queries
   - Update `handleQuerySuccess()` for both modes

4. **Tab State Management** (1.5 hours)
   - Implement hash-based staleness detection
   - Auto-clear logic when new query executes
   - Auto-refresh when switching to stale tab
   - Add visual stale indicators

5. **Helper Functions** (1.5 hours)
   - `formatSQL()` - Basic SQL formatting
   - `clearSQL()` - Clear editor with confirmation
   - `updateTabStates()` - Enable/disable tabs with indicators
   - `getQueryHash()` - Simple SQL hashing
   - `formatTimestamp()` - Relative time display

**Testing:**
- Test auto mode workflow end-to-end
- Test manual mode workflow end-to-end
- Test mode switching with/without SQL
- Test regenerate with confirmation
- Test tab staleness detection
- Test sessionStorage persistence
- Test error handling paths

---

### Phase 4: Integration Testing (Priority: High)

**Estimated Time: 4 hours**

1. **Workflow Testing** (2 hours)
   - Pure Auto mode: Question → Generate → Execute
   - Auto with Edit: Question → Generate → Edit → Execute
   - Pure Manual: Write SQL → Execute
   - Iterative refinement: Generate → Edit → Execute → Edit → Execute

2. **Cross-Feature Testing** (1 hour)
   - Analysis tab with auto-generated queries
   - Analysis tab with manual queries (no question)
   - Visualization tab with both query types
   - Tab switching and state persistence

3. **Error Scenario Testing** (1 hour)
   - Invalid SQL syntax
   - Dangerous SQL keywords
   - Timeout scenarios
   - Network errors
   - Empty query submissions

---

### Phase 5: Documentation (Priority: Medium)

**Estimated Time: 2 hours**

1. **User Documentation** (1 hour)
   - Update README.md with manual SQL editing section
   - Document mode switching
   - Explain workflow differences
   - List keyboard shortcuts

2. **Developer Documentation** (1 hour)
   - Document new API endpoint
   - Document state management approach
   - Update architecture diagrams
   - Document feature flag usage

---

## Total Estimated Implementation Time

| Phase | Time | Priority |
|-------|------|----------|
| Backend | 4 hours | High |
| HTML/CSS | 3 hours | High |
| JavaScript | 8 hours | High |
| Integration Testing | 4 hours | High |
| Documentation | 2 hours | Medium |
| **Total** | **21 hours** | **~3 days** |

---

## Success Criteria

### Must Have (MVP)
- ✅ Users can write SQL manually from scratch
- ✅ Users can edit AI-generated SQL before execution
- ✅ No breaking changes to existing auto-generation workflow
- ✅ Validation prevents dangerous SQL operations
- ✅ Error messages are clear and actionable
- ✅ Analysis and Visualization tabs work with both query types

### Should Have
- ✅ SQL state persists across page refreshes (sessionStorage)
- ✅ Mode switching preserves user work
- ✅ Stale tab indicators prevent confusion
- ✅ Query metadata visible in results
- ✅ Sanitized logging for debugging

### Nice to Have (Future Enhancements)
- ⏳ SQL syntax highlighting (CodeMirror/Monaco)
- ⏳ Auto-completion for table/column names
- ⏳ Query history (last 10 queries)
- ⏳ Save favorite queries
- ⏳ SQL explain plan viewer
- ⏳ Multi-query support (semicolon-separated)

---

## Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking existing workflow | High | Low | Thorough testing, backward compatibility design |
| Users write dangerous SQL | High | Low | Strict backend validation, clear error messages |
| Tab state confusion | Medium | Medium | Hash tracking, auto-clear, visual indicators |
| Performance degradation | Low | Low | 30s timeout, rate limiting, connection pooling |
| Increased support burden | Low | Medium | Clear error messages, good documentation |

---

## Dependencies & Prerequisites

### Required
- ✅ FastAPI (existing)
- ✅ Pydantic (existing)
- ✅ Python 3.8+ (existing)
- ✅ SQL Server connection (existing)

### New Dependencies
- `slowapi` - For rate limiting (install via pip)

### Optional
- `sql-formatter` (JavaScript) - For better SQL formatting
- CodeMirror or Monaco Editor - For syntax highlighting (future)

---

## Testing Checklist

### Backend Tests
- [ ] `/api/execute-sql` accepts valid SELECT queries
- [ ] `/api/execute-sql` rejects INSERT/UPDATE/DELETE
- [ ] `/api/execute-sql` rejects SQL injection attempts
- [ ] `/api/execute-sql` handles timeout correctly
- [ ] `/api/execute-sql` returns consistent error format
- [ ] Rate limiting enforces 30 req/min limit
- [ ] Logging sanitizes sensitive data
- [ ] Analysis endpoint works with optional question

### Frontend Tests
- [ ] Mode switching preserves SQL
- [ ] Generate button creates SQL in editor
- [ ] Execute button works in both modes
- [ ] SQL editor accepts manual input
- [ ] Regenerate shows confirmation if edited
- [ ] sessionStorage persists state across refresh
- [ ] Tab staleness detection works
- [ ] Query metadata displays correctly
- [ ] Error messages display properly
- [ ] Keyboard shortcuts work (Ctrl+Enter)

### Integration Tests
- [ ] Auto mode end-to-end workflow
- [ ] Manual mode end-to-end workflow
- [ ] Edit-then-execute workflow
- [ ] Analysis tab with manual queries
- [ ] Visualization tab with manual queries
- [ ] Cross-tab state synchronization
- [ ] Multiple query execution cycles

---

## Key Clarifications Documented

### User Preferences
1. **Validation:** Backend-only, no frontend validation, no IntelliSense
2. **Result Limits:** Not enforced - trust specialist user
3. **Security:** Local dev only, localhost binding, no authentication
4. **Deployment:** Single user, personal development environment

### Design Decisions
1. **Mode Preservation:** SQL always persists across mode switches
2. **Button Workflow:** Separate Generate and Execute buttons (review-before-execute)
3. **Tab Behavior:** Auto-clear on new query, visual stale indicators
4. **Analysis Strategy:** Works for both modes with optional question parameter
5. **Logging:** Sanitized to protect sensitive values while maintaining debuggability

### Technical Choices
1. **State Management:** sessionStorage for persistence (not localStorage)
2. **Hash Tracking:** Simple btoa() for query identity
3. **Rate Limiting:** 30 req/min via slowapi
4. **Timeout:** 30 seconds via asyncio.wait_for()
5. **Feature Flag:** localStorage toggle for easy enable/disable

---

## Next Steps

1. **Review & Approve:** Stakeholder review of this elicitation report
2. **Sprint Planning:** Break implementation into sprint-sized tasks
3. **Development:** Follow phased implementation plan (Phases 1-5)
4. **Testing:** Execute comprehensive test checklist
5. **Deployment:** Deploy to local environment
6. **Monitor:** Track usage and error rates
7. **Iterate:** Collect feedback and implement enhancements

---

## Appendix A: Quick Reference

### Key Files Modified
```
static/app.js          - State management, execution logic
static/index.html      - Mode selector, SQL editor UI
static/styles.css      - New component styling
app/main.py            - New /api/execute-sql endpoint
app/analysis_service.py - Optional question parameter
```

### New API Endpoints
```
POST /api/execute-sql
  Request: { sql: string }
  Response: QueryResponse (same as /api/query)
```

### New State Properties
```javascript
appState.sql = {
    mode: "auto" | "manual",
    query: string,
    originalGenerated: string,
    isEdited: boolean,
    lastExecutionTime: timestamp
}
```

### Keyboard Shortcuts
- `Ctrl+Enter` - Execute SQL (when editor focused)

---

## Document Control

**Version:** 1.0  
**Status:** Final - Approved  
**Approval Date:** January 10, 2025  
**Next Review:** Post-Implementation Retrospective  

**Change History:**
- v1.0 (2025-01-10) - Initial comprehensive elicitation report

---

**End of Report**
