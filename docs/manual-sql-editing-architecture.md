# Manual SQL Editing Feature - Architecture Document

**Project:** SQL Chatbot V2  
**Feature:** Manual SQL Editing Capability  
**Architect:** Winston (Holistic System Architect)  
**Date:** January 10, 2025  
**Version:** 1.0  
**Status:** Ready for Implementation

---

## Executive Summary

This architecture document defines the technical approach for adding manual SQL editing capabilities to the SQL Chatbot application. The feature enables users to write SQL queries manually from scratch or edit AI-generated SQL before execution, while maintaining backward compatibility with the existing auto-generation workflow.

### Key Architectural Decisions

- **Dual-Mode System**: Parallel Auto and Manual modes with seamless transition
- **Backend-Only Validation**: Single source of truth for security validation
- **Unified Response Schema**: Consistent API response format across endpoints
- **State Preservation**: SQL persists across mode switches via sessionStorage
- **Progressive Enhancement**: No breaking changes to existing functionality
- **Localhost Security**: Simplified security model for local development

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [API Design](#api-design)
4. [Frontend Architecture](#frontend-architecture)
5. [Security Architecture](#security-architecture)
6. [Data Flow](#data-flow)
7. [State Management](#state-management)
8. [Integration Points](#integration-points)
9. [Implementation Phases](#implementation-phases)
10. [Testing Strategy](#testing-strategy)

---

## Architecture Overview

### Current Architecture

```
┌─────────────┐
│   Browser   │
│  (HTML/JS)  │
└──────┬──────┘
       │ POST /api/query {question}
       ▼
┌─────────────┐
│   FastAPI   │
│   Backend   │
└──┬────┬─────┘
   │    │
   │    └──────► OpenAI GPT-5 API
   │            (Generate SQL)
   ▼
┌─────────────┐
│ SQL Server  │
│AdventureWorks│
└─────────────┘
```

### Enhanced Architecture (With Manual SQL Editing)

```
┌───────────────────────────────────────────────┐
│              Browser Frontend                  │
│  ┌──────────────┐      ┌──────────────┐      │
│  │  Auto Mode   │      │ Manual Mode  │      │
│  │ (Question)   │      │ (SQL Editor) │      │
│  └──────┬───────┘      └──────┬───────┘      │
│         │                     │               │
│         └────────┬────────────┘               │
│                  │                            │
│         ┌────────▼─────────┐                 │
│         │  SQL Editor      │                 │
│         │  (Editable)      │                 │
│         └────────┬─────────┘                 │
│                  │                            │
│         ┌────────▼─────────┐                 │
│         │  Execute Button  │                 │
│         └────────┬─────────┘                 │
└──────────────────┼──────────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
       │ Auto Mode │           │ Manual Mode
       ▼           │           ▼
┌─────────────┐    │    ┌──────────────┐
│ POST /api/  │    │    │ POST /api/   │
│   query     │    │    │ execute-sql  │
└──────┬──────┘    │    └──────┬───────┘
       │           │           │
       │           │           │
       ▼           │           │
┌─────────────┐    │           │
│  OpenAI     │    │           │
│  GPT-5 API  │    │           │
└──────┬──────┘    │           │
       │           │           │
       └───────────┴───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │  SQL Validation       │
       │  (_is_safe_select)    │
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │  SQL Execution        │
       │  (execute_sql_query)  │
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │  SQL Server           │
       │  AdventureWorks2022   │
       └───────────────────────┘
```

### Architectural Patterns

- **Pattern**: 3-Tier Web Application (Presentation, Business Logic, Data)
- **Frontend Pattern**: Single-Page Application with component-based UI
- **Backend Pattern**: RESTful API with endpoint specialization
- **State Pattern**: Client-side state management with persistence
- **Security Pattern**: Defense in depth (client validation + server validation)

---

## System Components

### 1. Frontend Components

#### 1.1 Mode Selector Component
**Purpose**: Toggle between Auto and Manual modes

**Responsibilities**:
- Display mode selection buttons (Auto/Manual)
- Handle mode switch events
- Preserve SQL across transitions
- Update UI visibility based on mode

**Technology**: Vanilla JavaScript + CSS

**State Management**:
```javascript
appState.sql.mode = "auto" | "manual"
```

#### 1.2 SQL Editor Component
**Purpose**: Editable SQL textarea with validation feedback

**Responsibilities**:
- Display SQL (generated or manual)
- Accept user input
- Show visual indicators (edited, valid, error)
- Provide formatting and clearing utilities
- Track edit state

**Technology**: HTML `<textarea>` with JavaScript event handlers

**State Management**:
```javascript
appState.sql = {
    query: string,              // Current SQL
    originalGenerated: string,  // Last AI-generated SQL
    isEdited: boolean,          // User modified?
    isValid: boolean,           // Passes validation?
    validationMessage: string   // Feedback message
}
```

#### 1.3 Execution Controls Component
**Purpose**: Control query generation and execution

**Responsibilities**:
- "Generate SQL" button (Auto mode)
- "Execute SQL" button (Both modes)
- "Regenerate" button (Auto mode with edited SQL)
- Enable/disable based on state
- Show loading indicators

**Technology**: Vanilla JavaScript with async/await

#### 1.4 Query Metadata Bar Component
**Purpose**: Display query context information

**Responsibilities**:
- Show mode (AI Generated vs Manual)
- Display original question (if available)
- Show execution timestamp
- Display row count

**Technology**: HTML + JavaScript template rendering

### 2. Backend Components

#### 2.1 Query Generation Endpoint
**Existing**: `POST /api/query`

**Modifications**: None (maintains backward compatibility)

**Responsibilities**:
- Accept natural language question
- Call OpenAI API for SQL generation
- Execute generated SQL
- Return unified response

#### 2.2 Manual SQL Execution Endpoint (NEW)
**New**: `POST /api/execute-sql`

**Responsibilities**:
- Accept user-provided SQL
- Validate SQL safety
- Execute against database
- Return unified response
- Log execution with sanitized SQL

**Implementation Location**: `app/main.py`

**Request Model**:
```python
class ExecuteSQLRequest(BaseModel):
    sql: str
```

**Response Model**:
```python
class QueryResponse(BaseModel):
    sql_query: str
    question: Optional[str] = None
    results: QueryResults
    execution_time_ms: Optional[float] = None
    row_count: int
    error: Optional[str] = None
    error_code: Optional[str] = None
```

#### 2.3 SQL Validation Service
**Existing**: `services._is_safe_select()`

**Modifications**: Make publicly accessible (remove underscore prefix)

**Responsibilities**:
- Validate SELECT-only queries
- Block dangerous keywords (DROP, DELETE, UPDATE, etc.)
- Prevent SQL injection attempts
- Allow safe CTEs (WITH clause)
- Prevent multiple statements

**Location**: `app/services.py`

#### 2.4 SQL Execution Service
**Existing**: `services.execute_sql_query()`

**Modifications**: Add timeout and error handling improvements

**Responsibilities**:
- Execute SQL against SQL Server
- Handle connection pooling
- Enforce 30-second timeout
- Return structured results or errors

**Location**: `app/services.py`

#### 2.5 Analysis Service Integration
**Existing**: `analysis_service.analyze_query_results()`

**Modifications**: Make `question` parameter optional

**Responsibilities**:
- Generate statistical analysis
- Support both auto and manual queries
- Adapt analysis quality based on available context

**Location**: `app/analysis_service.py`

### 3. Database Components

**No Changes Required**

Existing database connection and query execution mechanisms remain unchanged.

---

## API Design

### Unified Response Schema

All query endpoints return the same structure for consistency:

```typescript
interface QueryResponse {
    sql_query: string;                    // Executed SQL
    question?: string;                    // Original question (null for manual)
    results: {
        columns: string[];
        rows: Record<string, any>[];
    };
    execution_time_ms?: number;           // Query execution time
    row_count: number;                    // Number of rows returned
    error?: string;                       // Error message if failed
    error_code?: string;                  // Error type code
}
```

### Error Codes

Standardized error codes for client-side handling:

```typescript
type ErrorCode = 
    | "VALIDATION_FAILED"    // Invalid SQL syntax or unsafe query
    | "DB_ERROR"             // Database execution error
    | "TIMEOUT"              // Query exceeded 30 seconds
    | "INTERNAL_ERROR";      // Server error
```

### Endpoint Specifications

#### 1. Generate and Execute SQL (Existing)

```http
POST /api/query
Content-Type: application/json

{
    "question": "Show me top 10 employees by salary"
}
```

**Response** (Success):
```json
{
    "sql_query": "SELECT TOP 10 ...",
    "question": "Show me top 10 employees by salary",
    "results": {
        "columns": ["EmployeeID", "Salary"],
        "rows": [{"EmployeeID": 1, "Salary": 75000}, ...]
    },
    "execution_time_ms": 45.23,
    "row_count": 10
}
```

**Response** (Error):
```json
{
    "sql_query": "SELECT ...",
    "question": "...",
    "results": {
        "columns": [],
        "rows": []
    },
    "error": "Connection timeout",
    "error_code": "DB_ERROR"
}
```

#### 2. Execute Manual SQL (NEW)

```http
POST /api/execute-sql
Content-Type: application/json

{
    "sql": "SELECT FirstName, LastName FROM Person.Person WHERE BusinessEntityID = 5"
}
```

**Response** (Success):
```json
{
    "sql_query": "SELECT FirstName, LastName FROM Person.Person WHERE BusinessEntityID = 5",
    "question": null,
    "results": {
        "columns": ["FirstName", "LastName"],
        "rows": [{"FirstName": "John", "LastName": "Doe"}]
    },
    "execution_time_ms": 12.45,
    "row_count": 1
}
```

**Response** (Validation Error):
```json
{
    "sql_query": "DELETE FROM Person.Person",
    "question": null,
    "results": {
        "columns": [],
        "rows": []
    },
    "error": "Only SELECT statements are allowed. No data modification operations permitted.",
    "error_code": "VALIDATION_FAILED"
}
```

#### 3. Analyze Results (Modified)

```http
POST /api/analyze
Content-Type: application/json

{
    "columns": ["FirstName", "LastName", "Salary"],
    "rows": [{...}, {...}, ...]
}
```

**No change to endpoint structure**, but implementation now supports queries without associated questions.

---

## Frontend Architecture

### Component Hierarchy

```
┌──────────────────────────────────────────┐
│           SQL Chatbot Page               │
├──────────────────────────────────────────┤
│  ┌────────────────────────────────────┐  │
│  │      Mode Selector                 │  │
│  │  [Auto Mode] [Manual Mode]         │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Natural Language Input            │  │
│  │  (visible in Auto mode)            │  │
│  │  ┌──────────────────────────────┐  │  │
│  │  │ <textarea> Question          │  │  │
│  │  └──────────────────────────────┘  │  │
│  │  [Generate SQL Button]             │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  SQL Editor                        │  │
│  │  ┌──────────────────────────────┐  │  │
│  │  │ <textarea> SQL Query         │  │  │
│  │  │ (editable)                   │  │  │
│  │  └──────────────────────────────┘  │  │
│  │  Status: [✓ Valid SELECT]          │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Execution Controls                │  │
│  │  [Execute SQL] [Regenerate]        │  │
│  │  [Format] [Clear]                  │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Query Metadata Bar                │  │
│  │  Mode: 🤖 | Executed: Just now     │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Tab Navigation                    │  │
│  │  [Results] [Analysis] [Visualize]  │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Tab Content Area                  │  │
│  │  (Results/Analysis/Visualizations) │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

### State Management Architecture

#### Global State Structure

```javascript
const appState = {
    // New SQL editing state
    sql: {
        mode: "auto" | "manual",
        query: string,
        originalGenerated: string,
        lastSuccessfulQuery: string,
        isEdited: boolean,
        isValid: boolean,
        validationMessage: string,
        lastExecutionTime: timestamp
    },
    
    // Enhanced query state
    currentQuery: {
        question: string | null,
        sql: string,
        results: {
            columns: string[],
            rows: object[]
        },
        timestamp: timestamp,
        executionMode: "auto" | "manual",
        executionTimeMs: number,
        rowCount: number
    },
    
    // Existing states (unchanged)
    analysis: { ... },
    visualization: { ... },
    ui: { activeTab: string }
};
```

#### State Persistence

**Strategy**: sessionStorage for query session persistence

```javascript
// Save state on every significant change
function saveToSessionStorage() {
    sessionStorage.setItem('sql_state', JSON.stringify({
        mode: appState.sql.mode,
        query: appState.sql.query,
        originalGenerated: appState.sql.originalGenerated
    }));
}

// Restore state on page load
function restoreFromSessionStorage() {
    const saved = sessionStorage.getItem('sql_state');
    if (saved) {
        const state = JSON.parse(saved);
        appState.sql.mode = state.mode || 'auto';
        appState.sql.query = state.query || '';
        appState.sql.originalGenerated = state.originalGenerated || '';
    }
}
```

### Event Flow Diagrams

#### Auto Mode Flow

```
User enters question
       │
       ▼
Click "Generate SQL"
       │
       ▼
Call /api/query ────► OpenAI API
       │                   │
       │                   ▼
       │              Return SQL
       │                   │
       ▼◄──────────────────┘
SQL loaded to editor
       │
       ▼
User can edit (optional)
       │
       ▼
Click "Execute SQL"
       │
       ▼
Display results in tabs
```

#### Manual Mode Flow

```
User switches to Manual mode
       │
       ▼
User writes SQL in editor
       │
       ▼
Client-side validation
       │
       ▼
Click "Execute SQL"
       │
       ▼
Call /api/execute-sql
       │
       ▼
Server validates SQL
       │
       ├──► Invalid: Return error
       │
       └──► Valid: Execute query
                 │
                 ▼
            Return results
                 │
                 ▼
       Display results in tabs
```

#### Mode Switching Flow

```
User clicks mode button
       │
       ▼
Check if SQL exists in editor
       │
       ├──► Empty: Switch immediately
       │
       └──► Has SQL
              │
              ▼
       Manual → Auto?
              │
              ├──► Yes: Confirm if edited
              │         │
              │         ▼
              │    User confirms
              │         │
              └─────────┘
                        │
                        ▼
                 Switch mode
                        │
                        ▼
                Preserve SQL
                        │
                        ▼
                  Update UI
```

---

## Security Architecture

### Defense in Depth Strategy

```
┌─────────────────────────────────────────┐
│         Security Layer 1                │
│      Client-Side Validation             │
│  (Quick feedback, NOT security)         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         Security Layer 2                │
│      Server-Side Validation             │
│  (Single source of truth)               │
│  - _is_safe_select() validation         │
│  - Block dangerous keywords             │
│  - Prevent SQL injection                │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         Security Layer 3                │
│      Database Layer                     │
│  - Read-only connection pool            │
│  - Query timeout (30s)                  │
│  - Error handling                       │
└─────────────────────────────────────────┘
```

### SQL Validation Rules

**Implemented in**: `app/services.py::_is_safe_select()`

```python
def _is_safe_select(sql: str) -> bool:
    """
    Validate that SQL is a safe SELECT statement only.
    
    Rules:
    1. Must start with SELECT or WITH (CTE)
    2. No dangerous keywords:
       - drop, delete, update, insert
       - alter, create, truncate
       - exec, execute, sp_, xp_
       - Comment injection (--, /*, */)
    3. No multiple statements (no semicolons except at end)
    4. Case-insensitive matching
    
    Returns:
        True if safe, False otherwise
    """
```

### Network Security

**Deployment Context**: Localhost only

```python
# In production startup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",  # Localhost only
        port=8000
    )
```

**CORS Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)
```

### Rate Limiting

**Implementation**: Using `slowapi` library

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/execute-sql")
@limiter.limit("30/minute")
async def execute_sql(request: Request, sql_request: ExecuteSQLRequest):
    # Implementation...
```

### Logging Security

**Sanitized Logging** to prevent sensitive data exposure:

```python
import hashlib
import re

def sanitize_sql_for_logging(sql: str, max_length: int = 100) -> str:
    """Remove sensitive values from SQL for safe logging."""
    # Replace string literals
    sanitized = re.sub(r"'[^']*'", "'<STRING>'", sql)
    # Replace large numbers (potential IDs)
    sanitized = re.sub(r'\b\d{9,}\b', '<NUMBER>', sanitized)
    # Truncate
    return sanitized[:max_length] + ("..." if len(sanitized) > max_length else "")

def get_sql_hash(sql: str) -> str:
    """Generate hash for query tracking."""
    return hashlib.sha256(sql.encode()).hexdigest()[:16]

# Usage in endpoint
logger.info(
    f"MANUAL_SQL_START | IP: {client_ip} | "
    f"HASH: {get_sql_hash(sql)} | "
    f"SQL: {sanitize_sql_for_logging(sql)}"
)
```

---

## Data Flow

### Complete Data Flow Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ (1) User action
       │
       ▼
┌─────────────────────────────────┐
│  JavaScript Event Handler       │
│  - validateSQL()                │
│  - prepareRequest()             │
└──────┬──────────────────────────┘
       │
       │ (2) HTTP Request
       │     POST /api/execute-sql
       │     { sql: "SELECT ..." }
       │
       ▼
┌─────────────────────────────────┐
│  FastAPI Endpoint               │
│  @app.post("/api/execute-sql")  │
└──────┬──────────────────────────┘
       │
       │ (3) Validate request
       │
       ▼
┌─────────────────────────────────┐
│  SQL Validation Service         │
│  _is_safe_select(sql)           │
└──────┬──────────────────────────┘
       │
       ├──► (4a) Invalid
       │    Return error response
       │
       └──► (4b) Valid
              │
              ▼
       ┌──────────────────────────┐
       │  SQL Execution Service   │
       │  execute_sql_query()     │
       └──────┬───────────────────┘
              │
              │ (5) Execute query
              │
              ▼
       ┌──────────────────────────┐
       │  SQL Server Database     │
       │  AdventureWorks2022      │
       └──────┬───────────────────┘
              │
              │ (6) Results
              │
              ▼
       ┌──────────────────────────┐
       │  Format Response         │
       │  QueryResponse model     │
       └──────┬───────────────────┘
              │
              │ (7) JSON Response
              │
              ▼
       ┌──────────────────────────┐
       │  JavaScript Handler      │
       │  handleQuerySuccess()    │
       └──────┬───────────────────┘
              │
              │ (8) Update UI
              │
              ▼
       ┌──────────────────────────┐
       │  DOM Update              │
       │  - Results table         │
       │  - Analysis tab          │
       │  - Visualization tab     │
       └──────────────────────────┘
```

### Sequence Diagram: Manual SQL Execution

```
User          Browser         FastAPI        Validation      SQL Server
 │               │               │               │               │
 │ Write SQL     │               │               │               │
 │──────────────>│               │               │               │
 │               │               │               │               │
 │ Click Execute │               │               │               │
 │──────────────>│               │               │               │
 │               │               │               │               │
 │               │ POST          │               │               │
 │               │ /execute-sql  │               │               │
 │               │──────────────>│               │               │
 │               │               │               │               │
 │               │               │ Validate SQL  │               │
 │               │               │──────────────>│               │
 │               │               │               │               │
 │               │               │ Valid?        │               │
 │               │               │<──────────────│               │
 │               │               │               │               │
 │               │               │ Execute       │               │
 │               │               │──────────────────────────────>│
 │               │               │               │               │
 │               │               │               │  Query DB     │
 │               │               │               │               │
 │               │               │  Results      │               │
 │               │               │<──────────────────────────────│
 │               │               │               │               │
 │               │  Response     │               │               │
 │               │<──────────────│               │               │
 │               │               │               │               │
 │  Display      │               │               │               │
 │<──────────────│               │               │               │
 │  Results      │               │               │               │
```

---

## State Management

### State Transition Diagram

```
                    ┌──────────┐
                    │  Initial │
                    │  State   │
                    └─────┬────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
       ┌──────────┐            ┌──────────┐
       │   Auto   │            │  Manual  │
       │   Mode   │            │   Mode   │
       └─────┬────┘            └─────┬────┘
             │                       │
             │  Generate SQL         │  Write SQL
             ▼                       ▼
       ┌──────────┐            ┌──────────┐
       │   SQL    │◄───────────│   SQL    │
       │ Generated│   Edit     │  Manual  │
       └─────┬────┘            └─────┬────┘
             │                       │
             │                       │
             └───────────┬───────────┘
                         │
                         │  Execute
                         ▼
                   ┌──────────┐
                   │ Results  │
                   │ Display  │
                   └─────┬────┘
                         │
                ┌────────┼────────┐
                │        │        │
                ▼        ▼        ▼
         ┌──────┐  ┌────────┐  ┌──────┐
         │Result│  │Analysis│  │ Viz  │
         │ Tab  │  │  Tab   │  │ Tab  │
         └──────┘  └────────┘  └──────┘
```

### State Persistence Strategy

**Storage Mechanism**: sessionStorage (not localStorage)

**Rationale**:
- Persists during page refreshes
- Clears when browser tab closes
- Separate state per tab
- No cross-session pollution

**What to Persist**:
```javascript
{
    sql_mode: "auto" | "manual",
    last_sql: string,
    last_question: string,
    last_execution_timestamp: number
}
```

**What NOT to Persist**:
- Query results (too large)
- Analysis data (regenerate on demand)
- Visualization data (regenerate on demand)

---

## Integration Points

### 1. Analysis Feature Integration

**Challenge**: Analysis service expects original question for context

**Solution**: Make question parameter optional

**Implementation**:

```python
# Before (required question)
class AnalyzeRequest(BaseModel):
    columns: list[str]
    rows: list[dict]
    question: str  # Required

# After (optional question)
class AnalyzeRequest(BaseModel):
    columns: list[str]
    rows: list[dict]
    question: Optional[str] = None  # Optional

# Adapt analysis logic
def analyze_query_results(columns, rows, question=None):
    if question:
        # Full context analysis
        prompt = f"Question: {question}\nSQL: {sql}\n..."
    else:
        # SQL-only analysis
        prompt = f"SQL: {sql}\nDescribe the data retrieved..."
```

**UI Indicator**:
```javascript
// Show indicator when analysis is in SQL-only mode
if (!appState.currentQuery.question) {
    analysisTabBtn.innerHTML = 'Analysis *';
    analysisTabBtn.title = 'Analysis based on SQL only (no question context)';
}
```

### 2. Visualization Feature Integration

**Challenge**: Does visualization need question context?

**Solution**: No changes needed - visualization is question-agnostic

**Rationale**: Visualization recommendations are based on:
- Column types (numeric, categorical, datetime)
- Data patterns
- Statistical properties

These are independent of the user's original question.

### 3. Tab State Management

**Challenge**: Prevent showing stale analysis/visualization after query changes

**Solution**: Hash-based staleness detection

**Implementation**:

```javascript
function getQueryHash(sql) {
    // Simple hash for query identity
    return btoa(sql).substring(0, 16);
}

function executeSQL(sql, question = null) {
    // Reset dependent states
    resetAnalysisState();
    resetVisualizationState();
    
    // Store query identity
    appState.currentQuery.hash = getQueryHash(sql);
    appState.currentQuery.sql = sql;
    appState.currentQuery.question = question;
    
    // Execute and store results...
}

// When switching to a tab, check staleness
function switchTab(tabName) {
    if (tabName === 'analysis' && appState.analysis.queryHash !== appState.currentQuery.hash) {
        // Clear stale analysis and refetch
        resetAnalysisState();
        fetchAnalysis();
    }
}
```

---

## Implementation Phases

### Phase 1: Backend Implementation (4-6 hours)

**Priority**: HIGH  
**Dependencies**: None

#### Tasks

1. **Create New Endpoint** (1.5 hours)
   - Add `ExecuteSQLRequest` model to `app/main.py`
   - Implement `POST /api/execute-sql` endpoint
   - Add rate limiting decorator
   - Implement error handling with error codes

2. **Enhance SQL Validation** (1 hour)
   - Review `services._is_safe_select()` function
   - Add any missing dangerous keyword checks
   - Add unit tests for validation

3. **Add Logging Infrastructure** (1.5 hours)
   - Implement `sanitize_sql_for_logging()` function
   - Implement `get_sql_hash()` function
   - Add structured logging to endpoint
   - Configure log format

4. **Testing** (1 hour)
   - Test valid SELECT queries
   - Test rejection of dangerous queries
   - Test timeout behavior
   - Test error response format

**Deliverables**:
- ✅ Working `/api/execute-sql` endpoint
- ✅ Comprehensive SQL validation
- ✅ Sanitized logging
- ✅ Unit tests

### Phase 2: Frontend HTML/CSS (3-4 hours)

**Priority**: HIGH  
**Dependencies**: None

#### Tasks

1. **HTML Structure Updates** (1.5 hours)
   - Add mode selector buttons
   - Replace `<pre>` with `<textarea>` for SQL
   - Add execution controls section
   - Add query metadata bar
   - Ensure semantic HTML and accessibility

2. **CSS Styling** (1.5 hours)
   - Style mode selector (active/inactive states)
   - Style SQL editor (focus, edited, error states)
   - Style execution controls
   - Style query metadata bar
   - Ensure responsive design

3. **Testing** (1 hour)
   - Test responsive layout on different screen sizes
   - Test keyboard navigation
   - Test focus states
   - Validate HTML and accessibility

**Deliverables**:
- ✅ Updated HTML structure
- ✅ Complete CSS styling
- ✅ Responsive and accessible UI

### Phase 3: Frontend JavaScript (8-10 hours)

**Priority**: HIGH  
**Dependencies**: Phase 2

#### Tasks

1. **State Management** (2 hours)
   - Extend `appState` with SQL properties
   - Implement `saveToSessionStorage()`
   - Implement `restoreFromSessionStorage()`
   - Add state initialization on page load

2. **Mode Switching Logic** (1.5 hours)
   - Implement `switchMode()` function
   - Handle SQL preservation
   - Update UI visibility
   - Add confirmation for edited SQL

3. **SQL Validation** (1.5 hours)
   - Implement `validateSQL()` function
   - Implement `updateSQLValidation()` function
   - Add real-time validation feedback
   - Enable/disable execute button

4. **Query Execution Flow** (2 hours)
   - Split existing query flow
   - Implement `generateSQL()` function
   - Implement `executeManualSQL()` function
   - Update `handleQuerySuccess()` for both modes

5. **Helper Functions** (1 hour)
   - Implement `formatSQL()` function
   - Implement `clearSQL()` function
   - Implement `getQueryHash()` function
   - Implement metadata display functions

6. **Event Handlers** (1 hour)
   - Wire up all button click handlers
   - Add keyboard shortcuts (Ctrl+Enter)
   - Add input event handlers
   - Test all interactions

7. **Testing** (1 hour)
   - Test auto mode workflow
   - Test manual mode workflow
   - Test mode switching
   - Test error handling

**Deliverables**:
- ✅ Complete state management
- ✅ Working mode switching
- ✅ SQL validation and execution
- ✅ All event handlers wired

### Phase 4: Integration Testing (4-5 hours)

**Priority**: HIGH  
**Dependencies**: Phases 1-3

#### Tasks

1. **Workflow Testing** (2 hours)
   - Test pure auto mode workflow
   - Test auto with edit workflow
   - Test pure manual workflow
   - Test iterative refinement

2. **Cross-Feature Testing** (1.5 hours)
   - Test analysis tab with auto queries
   - Test analysis tab with manual queries
   - Test visualization tab with both modes
   - Test tab switching and staleness

3. **Error Scenario Testing** (1 hour)
   - Test invalid SQL syntax
   - Test dangerous SQL keywords
   - Test timeout scenarios
   - Test network errors

4. **Performance Testing** (0.5 hours)
   - Test with large result sets
   - Test with complex queries
   - Verify timeout enforcement

**Deliverables**:
- ✅ All workflows tested and working
- ✅ Cross-feature integration verified
- ✅ Error handling validated
- ✅ Performance acceptable

### Phase 5: Documentation & Deployment (2-3 hours)

**Priority**: MEDIUM  
**Dependencies**: Phases 1-4

#### Tasks

1. **User Documentation** (1 hour)
   - Update README.md with manual SQL editing section
   - Document mode switching
   - Document keyboard shortcuts
   - Add troubleshooting section

2. **Developer Documentation** (1 hour)
   - Update architecture diagrams
   - Document new API endpoint
   - Document state management
   - Document feature flag

3. **Deployment** (1 hour)
   - Install `slowapi` dependency
   - Update requirements.txt
   - Deploy to local environment
   - Verify deployment

**Deliverables**:
- ✅ Updated user documentation
- ✅ Updated developer documentation
- ✅ Successful deployment

### Total Estimated Time: 21-28 hours (~3-4 days)

---

## Testing Strategy

### Unit Testing

#### Backend Unit Tests

**File**: `tests/test_services.py`

```python
import pytest
from app import services

def test_is_safe_select_valid_queries():
    assert services._is_safe_select("SELECT * FROM Person.Person")
    assert services._is_safe_select("select id, name from table")
    assert services._is_safe_select("WITH cte AS (SELECT 1) SELECT * FROM cte")

def test_is_safe_select_dangerous_queries():
    assert not services._is_safe_select("DROP TABLE Person.Person")
    assert not services._is_safe_select("DELETE FROM Person.Person")
    assert not services._is_safe_select("UPDATE Person.Person SET Name = 'x'")
    assert not services._is_safe_select("INSERT INTO Person.Person VALUES (1)")
    assert not services._is_safe_select("SELECT * FROM Person.Person; DROP TABLE x")
    assert not services._is_safe_select("SELECT * FROM Person.Person -- comment")

def test_sanitize_sql_for_logging():
    sql = "SELECT * FROM Person.Person WHERE Name = 'John Doe' AND ID = 123456789"
    sanitized = services.sanitize_sql_for_logging(sql)
    assert "<STRING>" in sanitized
    assert "<NUMBER>" in sanitized
    assert "John Doe" not in sanitized
    assert "123456789" not in sanitized

def test_get_sql_hash():
    sql1 = "SELECT * FROM Person.Person"
    sql2 = "SELECT * FROM Person.Person"
    sql3 = "SELECT * FROM Product.Product"
    
    hash1 = services.get_sql_hash(sql1)
    hash2 = services.get_sql_hash(sql2)
    hash3 = services.get_sql_hash(sql3)
    
    assert hash1 == hash2  # Same SQL = same hash
    assert hash1 != hash3  # Different SQL = different hash
    assert len(hash1) == 16  # Hash length
```

**File**: `tests/test_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_execute_sql_endpoint_valid():
    response = client.post(
        "/api/execute-sql",
        json={"sql": "SELECT TOP 5 * FROM Person.Person"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sql_query" in data
    assert "results" in data
    assert data["question"] is None

def test_execute_sql_endpoint_invalid():
    response = client.post(
        "/api/execute-sql",
        json={"sql": "DROP TABLE Person.Person"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error_code"] == "VALIDATION_FAILED"

def test_execute_sql_endpoint_rate_limit():
    # Make 31 requests to exceed limit
    for i in range(31):
        response = client.post(
            "/api/execute-sql",
            json={"sql": f"SELECT TOP 1 * FROM Person.Person WHERE ID = {i}"}
        )
        if i < 30:
            assert response.status_code == 200
        else:
            assert response.status_code == 429  # Rate limit exceeded
```

#### Frontend Unit Tests

**File**: `tests/frontend/test_state_management.js`

```javascript
describe('State Management', () => {
    beforeEach(() => {
        sessionStorage.clear();
        appState.sql = {
            mode: 'auto',
            query: '',
            originalGenerated: '',
            isEdited: false
        };
    });
    
    test('saveToSessionStorage stores state', () => {
        appState.sql.mode = 'manual';
        appState.sql.query = 'SELECT * FROM Person.Person';
        saveToSessionStorage();
        
        const stored = JSON.parse(sessionStorage.getItem('sql_state'));
        expect(stored.mode).toBe('manual');
        expect(stored.query).toBe('SELECT * FROM Person.Person');
    });
    
    test('restoreFromSessionStorage loads state', () => {
        sessionStorage.setItem('sql_state', JSON.stringify({
            mode: 'manual',
            query: 'SELECT * FROM Person.Person'
        }));
        
        restoreFromSessionStorage();
        expect(appState.sql.mode).toBe('manual');
        expect(appState.sql.query).toBe('SELECT * FROM Person.Person');
    });
    
    test('getQueryHash generates consistent hashes', () => {
        const hash1 = getQueryHash('SELECT * FROM Person.Person');
        const hash2 = getQueryHash('SELECT * FROM Person.Person');
        const hash3 = getQueryHash('SELECT * FROM Product.Product');
        
        expect(hash1).toBe(hash2);
        expect(hash1).not.toBe(hash3);
    });
});
```

### Integration Testing

#### Manual Testing Checklist

**Auto Mode Workflow**:
- [ ] Enter question, click Generate SQL
- [ ] SQL appears in editor
- [ ] Click Execute SQL
- [ ] Results display in Results tab
- [ ] Analysis tab loads correctly
- [ ] Visualization tab works correctly

**Manual Mode Workflow**:
- [ ] Switch to Manual mode
- [ ] Write SQL in editor
- [ ] Validation feedback appears
- [ ] Click Execute SQL
- [ ] Results display in Results tab
- [ ] Analysis tab loads (without question)
- [ ] Visualization tab works correctly

**Auto + Edit Workflow**:
- [ ] Generate SQL in Auto mode
- [ ] Edit the SQL
- [ ] Editor shows "edited" indicator
- [ ] Execute edited SQL
- [ ] Click Regenerate shows confirmation
- [ ] Confirm overwrites edited SQL

**Mode Switching**:
- [ ] Switch from Auto to Manual preserves SQL
- [ ] Switch from Manual to Auto preserves SQL
- [ ] Confirm shown when switching with edited SQL
- [ ] Cancel preserves current mode

**Error Handling**:
- [ ] Invalid SQL shows error message
- [ ] Dangerous SQL blocked with clear message
- [ ] Network error handled gracefully
- [ ] Timeout shows appropriate message

**State Persistence**:
- [ ] Refresh page preserves mode
- [ ] Refresh page preserves SQL
- [ ] Close tab clears sessionStorage
- [ ] New tab has fresh state

### Performance Testing

**Metrics to Track**:
- SQL generation time (should be < 10s)
- Query execution time (should be < 30s)
- Page load time (should be < 2s)
- State restoration time (should be < 100ms)
- UI responsiveness (no lag during typing)

**Load Testing**:
- Test with 100 row result set
- Test with 1,000 row result set
- Test with 10,000 row result set
- Verify visualization sampling works

---

## Success Criteria

### Must-Have (MVP)

✅ **Functional Requirements**:
- Users can write SQL manually from scratch
- Users can edit AI-generated SQL before execution
- No breaking changes to existing auto-generation workflow
- Validation prevents dangerous SQL operations
- Error messages are clear and actionable

✅ **Technical Requirements**:
- Backend validation is single source of truth
- Response format is consistent across endpoints
- SQL persists across mode switches
- Analysis and Visualization tabs work with both query types
- Logging is sanitized and secure

✅ **Non-Functional Requirements**:
- Query execution completes in < 30 seconds
- Page remains responsive during operations
- State persists across page refreshes
- Rate limiting prevents abuse

### Nice-to-Have (Future Enhancements)

⏳ **User Experience**:
- SQL syntax highlighting (CodeMirror/Monaco)
- Auto-completion for table/column names
- Query history (last 10 queries)
- Save favorite queries

⏳ **Advanced Features**:
- SQL explain plan viewer
- Multi-query support (semicolon-separated)
- Export query results to CSV
- Share queries via URL

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| Breaking existing workflow | **High** | **Low** | Comprehensive testing, maintain backward compatibility, feature flag |
| Users write dangerous SQL | **High** | **Low** | Strict backend validation, clear error messages, localhost-only deployment |
| Performance degradation | **Medium** | **Low** | Query timeout (30s), rate limiting (30 req/min), connection pooling |
| State management bugs | **Medium** | **Medium** | Thorough testing of all state transitions, simple state structure |
| Cross-browser compatibility | **Low** | **Low** | Use vanilla JS, avoid experimental features, test on major browsers |
| Increased support burden | **Low** | **Medium** | Clear documentation, intuitive UI, helpful error messages |

---

## Rollback Plan

If critical issues arise after deployment:

1. **Immediate Rollback**:
   - Set feature flag to disable manual editing
   - ```javascript
     localStorage.setItem('feature_manual_sql', 'false');
     ```
   - Reload page - reverts to auto-only mode

2. **Partial Rollback**:
   - Disable new endpoint via environment variable
   - Keep UI changes but disable manual execution
   - Users can still view/copy SQL

3. **Full Rollback**:
   - Git revert to previous commit
   - Redeploy previous version
   - Investigate issues before retry

---

## Deployment Checklist

### Pre-Deployment

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Backup current production code

### Deployment

- [ ] Install `slowapi` dependency: `pip install slowapi`
- [ ] Update `requirements.txt`
- [ ] Deploy backend changes
- [ ] Deploy frontend changes
- [ ] Restart application server

### Post-Deployment

- [ ] Verify `/api/execute-sql` endpoint responds
- [ ] Test auto mode workflow
- [ ] Test manual mode workflow
- [ ] Monitor error logs for issues
- [ ] Monitor rate limiting
- [ ] Collect initial user feedback

### Monitoring

- [ ] Track API endpoint response times
- [ ] Monitor error rates
- [ ] Track mode usage (auto vs manual)
- [ ] Monitor query execution times
- [ ] Track validation failure rates

---

## Conclusion

This architecture document provides a comprehensive blueprint for implementing manual SQL editing capabilities in the SQL Chatbot application. The design prioritizes:

1. **Backward Compatibility**: No breaking changes to existing functionality
2. **Security**: Multi-layer validation and sanitized logging
3. **User Experience**: Seamless mode switching and state preservation
4. **Maintainability**: Clean separation of concerns and consistent patterns
5. **Extensibility**: Foundation for future enhancements

The phased implementation approach ensures systematic progress with clear deliverables at each stage. The estimated 21-28 hours of development time represents approximately 3-4 days of focused work.

### Next Steps

1. **Review & Approval**: Stakeholder review of this architecture document
2. **Sprint Planning**: Break implementation into sprint-sized tasks
3. **Development**: Execute Phases 1-5 sequentially
4. **Testing**: Follow comprehensive testing strategy
5. **Deployment**: Deploy to local environment with monitoring
6. **Iteration**: Collect feedback and implement enhancements

---

## Appendix: File Modification Summary

### Files to Create

- `tests/test_services.py` - Backend unit tests
- `tests/test_api.py` - API endpoint tests

### Files to Modify

#### High Impact (Major Changes)

- `static/app.js` - State management, mode switching, execution flow
- `static/index.html` - Mode selector, SQL editor, execution controls
- `static/styles.css` - New UI component styling
- `app/main.py` - New `/api/execute-sql` endpoint

#### Medium Impact (Enhancements)

- `app/services.py` - Add logging functions, expose validation
- `requirements.txt` - Add `slowapi` dependency

#### Low Impact (Optional)

- `README.md` - Update with manual SQL editing documentation
- `docs/architecture.md` - Update with new features

---

**Document Version**: 1.0  
**Last Updated**: January 10, 2025  
**Status**: Ready for Implementation  
**Approved By**: [Pending Stakeholder Review]

---

**End of Architecture Document**
