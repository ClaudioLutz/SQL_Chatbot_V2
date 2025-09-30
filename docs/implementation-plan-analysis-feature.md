# Implementation Plan: Analysis Feature Development

**Based On:** Architecture Document Section 11 Implementation Checklist  
**Created:** 2025-09-30  
**Status:** Ready for Development  
**Developer:** @dev

---

## Overview

This document transforms the architecture checklist into actionable development tasks with clear dependencies, acceptance criteria, and estimated effort. Follow phases sequentially to ensure smooth integration.

**Total Estimated Effort:** 2-3 days  
**Risk Level:** Low  
**Complexity:** Medium

---

## Phase 1: Setup & Dependencies (0.5 hours)

### Task 1.1: Install Required Dependencies
**Priority:** CRITICAL  
**Depends On:** None  
**Estimated Time:** 10 minutes

**Actions:**
```bash
# Update requirements.txt
pip install skimpy==0.0.9
pip install pandas>=2.0.0
pip install numpy>=1.24.0
```

**Acceptance Criteria:**
- [ ] `skimpy` successfully imported in Python
- [ ] No version conflicts with existing dependencies
- [ ] `requirements.txt` updated with versions

**Verification:**
```python
# Test import
import skimpy
import pandas as pd
print(skimpy.__version__)  # Should be 0.0.9
```

---

### Task 1.2: Create Test Data Fixtures
**Priority:** HIGH  
**Depends On:** Task 1.1  
**Estimated Time:** 20 minutes

**Actions:**
```python
# Create tests/fixtures/analysis_test_data.py
"""Test fixtures for analysis feature."""

# Small dataset (typical case)
SMALL_DATASET = {
    "columns": ["ProductID", "Name", "ListPrice"],
    "rows": [
        {"ProductID": 1, "Name": "Product A", "ListPrice": 49.99},
        {"ProductID": 2, "Name": "Product B", "ListPrice": 29.99},
        # ... 10 total rows
    ]
}

# Large dataset (near limit)
LARGE_DATASET = {
    "columns": ["ID", "Value"],
    "rows": [{"ID": i, "Value": i * 1.5} for i in range(45000)]
}

# Too large dataset (exceeds limit)
TOO_LARGE_DATASET = {
    "columns": ["ID"],
    "rows": [{"ID": i} for i in range(60000)]
}

# Dataset with nulls
NULL_DATASET = {
    "columns": ["A", "B", "C"],
    "rows": [
        {"A": 1, "B": 2, "C": None},
        {"A": 2, "B": None, "C": 3},
    ]
}

# Mixed types dataset
MIXED_DATASET = {
    "columns": ["ID", "Name", "Price", "Date"],
    "rows": [
        {"ID": 1, "Name": "Item1", "Price": 10.5, "Date": "2024-01-01"},
        {"ID": 2, "Name": "Item2", "Price": 20.0, "Date": "2024-01-02"},
    ]
}

# Empty dataset
EMPTY_DATASET = {
    "columns": ["A"],
    "rows": []
}

# Single row (insufficient)
SINGLE_ROW_DATASET = {
    "columns": ["A", "B"],
    "rows": [{"A": 1, "B": 2}]
}
```

**Acceptance Criteria:**
- [ ] Test fixtures file created
- [ ] All 7 test scenarios covered
- [ ] Data structures match API format

---

## Phase 2: Backend Implementation (4-6 hours)

### Task 2.1: Create Analysis Service Module
**Priority:** CRITICAL  
**Depends On:** Task 1.1  
**Estimated Time:** 2 hours

**File:** `app/analysis_service.py`

**Implementation Steps:**

1. **Create module structure:**
```python
"""
Analysis service for generating statistical summaries using skimpy.
"""
import logging
from typing import Dict, List, Any, Tuple
import pandas as pd
from skimpy import skim

logger = logging.getLogger(__name__)

# Constants
MAX_ROWS = 50000
MIN_ROWS = 2
MIN_COLUMNS = 1
```

2. **Implement main entry point:**
```python
def analyze_query_results(columns: List[str], rows: List[Dict]) -> Dict[str, Any]:
    """
    Generate statistical analysis for query results.
    
    Args:
        columns: List of column names
        rows: List of row dictionaries
        
    Returns:
        Dict with status and analysis data or error info
    """
    logger.info(f"Starting analysis: {len(rows)} rows, {len(columns)} columns")
    
    # Validation
    is_valid, error_code = _validate_dataset_requirements(columns, rows)
    if not is_valid:
        return _create_error_response(error_code, len(rows), len(columns))
    
    try:
        # Convert to DataFrame
        df = _convert_to_dataframe(columns, rows)
        
        # Generate skimpy analysis
        skim_result = skim(df)
        
        # Extract structured data
        analysis = {
            "status": "success",
            "row_count": len(rows),
            "column_count": len(columns),
            "variable_types": _extract_variable_types(df),
            "numeric_stats": _extract_numeric_stats(df),
            "cardinality": _extract_cardinality(df),
            "missing_values": _extract_missing_values(df)
        }
        
        logger.info("Analysis completed successfully")
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Analysis could not be generated for this dataset.",
            "error_detail": str(e)
        }
```

3. **Implement validation:**
```python
def _validate_dataset_requirements(
    columns: List[str], 
    rows: List[Dict]
) -> Tuple[bool, str]:
    """
    Validate minimum dataset requirements.
    
    Returns:
        (is_valid, error_code)
    """
    if len(columns) < MIN_COLUMNS:
        return False, "no_columns"
    
    if len(rows) < MIN_ROWS:
        return False, "insufficient_rows"
    
    if len(rows) > MAX_ROWS:
        return False, "too_large"
    
    return True, None
```

4. **Implement helper functions:**
```python
def _create_error_response(
    error_code: str, 
    row_count: int, 
    column_count: int
) -> Dict[str, Any]:
    """Create appropriate error response based on error code."""
    messages = {
        "no_columns": "No columns to analyze.",
        "insufficient_rows": "Analysis requires at least 2 rows of data.",
        "too_large": "Analysis unavailable for datasets exceeding 50,000 rows. Please refine your query for detailed statistics."
    }
    
    response = {
        "status": error_code,
        "row_count": row_count,
        "column_count": column_count,
        "message": messages.get(error_code, "Unknown error")
    }
    
    return response

def _convert_to_dataframe(columns: List[str], rows: List[Dict]) -> pd.DataFrame:
    """Convert API data format to pandas DataFrame."""
    return pd.DataFrame(rows, columns=columns)

def _extract_variable_types(df: pd.DataFrame) -> Dict[str, int]:
    """Extract column type distribution."""
    type_counts = {
        "numeric": 0,
        "categorical": 0,
        "datetime": 0,
        "other": 0
    }
    
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            type_counts["numeric"] += 1
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            type_counts["datetime"] += 1
        elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_categorical_dtype(dtype):
            type_counts["categorical"] += 1
        else:
            type_counts["other"] += 1
    
    return type_counts

def _extract_numeric_stats(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract numeric column statistics."""
    stats = []
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    for col in numeric_cols:
        col_stats = {
            "column": col,
            "count": int(df[col].count()),
            "mean": float(df[col].mean()) if not df[col].isna().all() else None,
            "std": float(df[col].std()) if not df[col].isna().all() else None,
            "min": float(df[col].min()) if not df[col].isna().all() else None,
            "q25": float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
            "q50": float(df[col].quantile(0.50)) if not df[col].isna().all() else None,
            "q75": float(df[col].quantile(0.75)) if not df[col].isna().all() else None,
            "max": float(df[col].max()) if not df[col].isna().all() else None
        }
        stats.append(col_stats)
    
    return stats

def _extract_cardinality(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract unique value counts for each column."""
    cardinality = []
    
    for col in df.columns:
        cardinality.append({
            "column": col,
            "unique_count": int(df[col].nunique()),
            "total_count": len(df)
        })
    
    return cardinality

def _extract_missing_values(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract null/missing value analysis."""
    missing = []
    
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        total_count = len(df)
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
        
        missing.append({
            "column": col,
            "null_count": null_count,
            "null_percentage": round(null_percentage, 2)
        })
    
    return missing
```

**Acceptance Criteria:**
- [ ] `app/analysis_service.py` created
- [ ] All 10 functions implemented
- [ ] Validation for ≥2 rows and ≥1 column
- [ ] Row limit check (≤50,000)
- [ ] Error handling with try-catch
- [ ] Logging at key points
- [ ] Type hints for all functions
- [ ] Docstrings for all functions

**Testing:**
```python
# Manual verification
from app.analysis_service import analyze_query_results

# Test small dataset
result = analyze_query_results(
    columns=["A", "B"],
    rows=[{"A": 1, "B": 2}, {"A": 3, "B": 4}]
)
print(result["status"])  # Should be "success"
```

---

### Task 2.2: Add Analysis Endpoint to Main App
**Priority:** CRITICAL  
**Depends On:** Task 2.1  
**Estimated Time:** 30 minutes

**File:** `app/main.py`

**Actions:**

1. **Import analysis service:**
```python
from app import analysis_service
```

2. **Add Pydantic model:**
```python
class AnalyzeRequest(BaseModel):
    columns: list[str]
    rows: list[dict]
```

3. **Add endpoint:**
```python
@app.post("/api/analyze")
async def analyze_results(request: AnalyzeRequest):
    """
    Generate statistical analysis for query results.
    
    Request body:
        columns: List of column names
        rows: List of row dictionaries
        
    Returns:
        Analysis data with status: success/too_large/error
    """
    try:
        analysis = analysis_service.analyze_query_results(
            columns=request.columns,
            rows=request.rows
        )
        return analysis
    except Exception as e:
        logger.error(f"Analysis endpoint error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Analysis could not be generated for this dataset.",
            "error_detail": str(e)
        }
```

**Acceptance Criteria:**
- [ ] `/api/analyze` endpoint added
- [ ] Accepts POST requests
- [ ] Uses Pydantic validation
- [ ] Returns JSON response
- [ ] Error handling in place
- [ ] Async function for non-blocking

**Testing:**
```bash
# Test with curl
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["A", "B"],
    "rows": [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
  }'
```

---

### Task 2.3: Backend Unit Tests
**Priority:** HIGH  
**Depends On:** Task 2.1  
**Estimated Time:** 1.5 hours

**File:** `tests/test_analysis_service.py`

**Implementation:**
```python
"""Unit tests for analysis service."""
import pytest
from app.analysis_service import (
    analyze_query_results,
    _validate_dataset_requirements,
    _convert_to_dataframe,
    _extract_variable_types,
    _extract_numeric_stats,
    _extract_cardinality,
    _extract_missing_values
)
from tests.fixtures.analysis_test_data import (
    SMALL_DATASET,
    LARGE_DATASET,
    TOO_LARGE_DATASET,
    NULL_DATASET,
    MIXED_DATASET,
    EMPTY_DATASET,
    SINGLE_ROW_DATASET
)


class TestAnalyzeQueryResults:
    """Test main analyze_query_results function."""
    
    def test_valid_dataset(self):
        """Test analysis with valid dataset."""
        result = analyze_query_results(
            columns=SMALL_DATASET["columns"],
            rows=SMALL_DATASET["rows"]
        )
        assert result["status"] == "success"
        assert "variable_types" in result
        assert "numeric_stats" in result
        assert "cardinality" in result
        assert "missing_values" in result
    
    def test_row_limit_exceeded(self):
        """Test rejection of datasets > 50K rows."""
        result = analyze_query_results(
            columns=TOO_LARGE_DATASET["columns"],
            rows=TOO_LARGE_DATASET["rows"]
        )
        assert result["status"] == "too_large"
        assert "50,000 rows" in result["message"]
    
    def test_empty_dataset(self):
        """Test handling of empty dataset."""
        result = analyze_query_results(
            columns=EMPTY_DATASET["columns"],
            rows=EMPTY_DATASET["rows"]
        )
        assert result["status"] == "insufficient_rows"
    
    def test_single_row_dataset(self):
        """Test rejection of single row dataset."""
        result = analyze_query_results(
            columns=SINGLE_ROW_DATASET["columns"],
            rows=SINGLE_ROW_DATASET["rows"]
        )
        assert result["status"] == "insufficient_rows"
    
    def test_numeric_only(self):
        """Test analysis with only numeric columns."""
        data = {
            "columns": ["A", "B"],
            "rows": [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
        }
        result = analyze_query_results(data["columns"], data["rows"])
        assert result["status"] == "success"
        assert result["variable_types"]["numeric"] == 2
        assert len(result["numeric_stats"]) == 2
    
    def test_with_nulls(self):
        """Test analysis with missing values."""
        result = analyze_query_results(
            columns=NULL_DATASET["columns"],
            rows=NULL_DATASET["rows"]
        )
        assert result["status"] == "success"
        # Check that missing values are detected
        missing_data = result["missing_values"]
        assert any(m["null_count"] > 0 for m in missing_data)
    
    def test_mixed_types(self):
        """Test analysis with mixed data types."""
        result = analyze_query_results(
            columns=MIXED_DATASET["columns"],
            rows=MIXED_DATASET["rows"]
        )
        assert result["status"] == "success"
        var_types = result["variable_types"]
        assert var_types["numeric"] >= 1
        assert var_types["categorical"] >= 1


class TestValidation:
    """Test validation functions."""
    
    def test_valid_dataset(self):
        """Test validation passes for valid dataset."""
        is_valid, error = _validate_dataset_requirements(
            columns=["A", "B"],
            rows=[{"A": 1}, {"A": 2}]
        )
        assert is_valid is True
        assert error is None
    
    def test_no_columns(self):
        """Test validation fails for no columns."""
        is_valid, error = _validate_dataset_requirements(
            columns=[],
            rows=[{"A": 1}]
        )
        assert is_valid is False
        assert error == "no_columns"
    
    def test_insufficient_rows(self):
        """Test validation fails for < 2 rows."""
        is_valid, error = _validate_dataset_requirements(
            columns=["A"],
            rows=[{"A": 1}]
        )
        assert is_valid is False
        assert error == "insufficient_rows"
    
    def test_too_many_rows(self):
        """Test validation fails for > 50K rows."""
        is_valid, error = _validate_dataset_requirements(
            columns=["A"],
            rows=[{"A": i} for i in range(60000)]
        )
        assert is_valid is False
        assert error == "too_large"


class TestDataExtraction:
    """Test data extraction functions."""
    
    def test_extract_variable_types(self):
        """Test variable type extraction."""
        import pandas as pd
        df = pd.DataFrame({
            "num": [1, 2, 3],
            "cat": ["a", "b", "c"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
        })
        types = _extract_variable_types(df)
        assert types["numeric"] == 1
        assert types["categorical"] == 1
        assert types["datetime"] == 1
    
    def test_extract_numeric_stats(self):
        """Test numeric statistics extraction."""
        import pandas as pd
        df = pd.DataFrame({"A": [1, 2, 3, 4, 5]})
        stats = _extract_numeric_stats(df)
        assert len(stats) == 1
        assert stats[0]["column"] == "A"
        assert stats[0]["mean"] == 3.0
        assert stats[0]["min"] == 1.0
        assert stats[0]["max"] == 5.0
    
    def test_extract_cardinality(self):
        """Test cardinality extraction."""
        import pandas as pd
        df = pd.DataFrame({
            "A": [1, 1, 2, 2, 3],
            "B": [1, 2, 3, 4, 5]
        })
        card = _extract_cardinality(df)
        assert len(card) == 2
        assert card[0]["unique_count"] == 3
        assert card[1]["unique_count"] == 5
    
    def test_extract_missing_values(self):
        """Test missing values extraction."""
        import pandas as pd
        import numpy as np
        df = pd.DataFrame({
            "A": [1, 2, np.nan, 4, 5],
            "B": [1, 2, 3, 4, 5]
        })
        missing = _extract_missing_values(df)
        assert len(missing) == 2
        assert missing[0]["null_count"] == 1
        assert missing[0]["null_percentage"] == 20.0
        assert missing[1]["null_count"] == 0
```

**Acceptance Criteria:**
- [ ] Test file created
- [ ] 15+ test cases implemented
- [ ] All test scenarios covered
- [ ] Tests pass with `pytest`
- [ ] Code coverage > 90%

**Run Tests:**
```bash
pytest tests/test_analysis_service.py -v
pytest tests/test_analysis_service.py --cov=app.analysis_service
```

---

### Task 2.4: Backend Integration Tests
**Priority:** HIGH  
**Depends On:** Task 2.2  
**Estimated Time:** 1 hour

**File:** `tests/test_analyze_endpoint.py`

**Implementation:**
```python
"""Integration tests for /api/analyze endpoint."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.fixtures.analysis_test_data import SMALL_DATASET, TOO_LARGE_DATASET

client = TestClient(app)


class TestAnalyzeEndpoint:
    """Test /api/analyze endpoint."""
    
    def test_analyze_success(self):
        """Test successful analysis."""
        response = client.post("/api/analyze", json=SMALL_DATASET)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "variable_types" in data
    
    def test_analyze_too_large(self):
        """Test rejection of large dataset."""
        response = client.post("/api/analyze", json=TOO_LARGE_DATASET)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "too_large"
    
    def test_analyze_invalid_request(self):
        """Test invalid request format."""
        response = client.post("/api/analyze", json={"invalid": "data"})
        assert response.status_code == 422  # Pydantic validation error
    
    def test_analyze_empty_body(self):
        """Test empty request body."""
        response = client.post("/api/analyze", json={})
        assert response.status_code == 422
```

**Acceptance Criteria:**
- [ ] Integration tests file created
- [ ] 4+ endpoint tests implemented
- [ ] Tests cover success and error cases
- [ ] Tests pass with `pytest`

---

## Phase 3: Frontend Implementation (4-5 hours)

### Task 3.1: Update HTML Structure
**Priority:** CRITICAL  
**Depends On:** None (can run parallel to backend)  
**Estimated Time:** 30 minutes

**File:** `static/index.html`

**Actions:**

1. **Add tab structure after SQL output:**
```html
<!-- Existing SQL output remains -->
<hr>
<h2>Generated SQL Query:</h2>
<pre id="sql-query-output"></pre>

<!-- NEW: Tab Navigation -->
<div class="tab-container">
    <button class="tab-button active" data-tab="results" id="results-tab-btn">
        Results
    </button>
    <button class="tab-button" data-tab="analysis" id="analysis-tab-btn">
        Analysis
    </button>
</div>

<!-- NEW: Results Tab Content -->
<div id="results-tab" class="tab-content active">
    <h2>Results:</h2>
    <div id="results-output"></div>
</div>

<!-- NEW: Analysis Tab Content -->
<div id="analysis-tab" class="tab-content">
    <h2>Statistical Analysis:</h2>
    <div id="analysis-loading" class="loading-indicator">
        <span class="spinner"></span> Generating analysis...
    </div>
    <div id="analysis-output"></div>
    <div id="analysis-error" class="error-message" style="display: none;"></div>
</div>
```

**Acceptance Criteria:**
- [ ] Tab buttons added
- [ ] Tab content containers added
- [ ] Loading indicator added
- [ ] Error message container added
- [ ] Maintains existing Results display

---

### Task 3.2: Add CSS Styles
**Priority:** HIGH  
**Depends On:** Task 3.1  
**Estimated Time:** 30 minutes

**File:** `static/styles.css`

**Add Styles:**
```css
/* Tab Container */
.tab-container {
    display: flex;
    border-bottom: 2px solid #ddd;
    margin-top: 20px;
    margin-bottom: 0;
}

.tab-button {
    background-color: #f5f5f5;
    border: none;
    border-bottom: 3px solid transparent;
    padding: 12px 24px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.3s ease;
    color: #666;
}

.tab-button:hover {
    background-color: #e8e8e8;
    color: #333;
}

.tab-button.active {
    background-color: white;
    border-bottom: 3px solid #007bff;
    color: #007bff;
    font-weight: 600;
}

.tab-button:disabled {
    background-color: #f5f5f5;
    color: #999;
    cursor: not-allowed;
    opacity: 0.6;
}

/* Tab Content */
.tab-content {
    display: none;
    padding: 20px;
    border: 1px solid #ddd;
    border-top: none;
    background-color: white;
    min-height: 200px;
}

.tab-content.active {
    display: block;
}

/* Loading Indicator */
.loading-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
    color: #666;
}

.spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 10px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Analysis Display */
.analysis-section {
    margin-bottom: 30px;
}

.analysis-section h3 {
    color: #333;
    border-bottom: 2px solid #007bff;
    padding-bottom: 8px;
    margin-bottom: 15px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}

.stat-card {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 15px;
}

.stat-card .stat-label {
    font-size: 12px;
    color: #666;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 5px;
}

.stat-card .stat-value {
    font-size: 24px;
    color: #007bff;
    font-weight: bold;
}

/* Analysis Tables */
.analysis-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

.analysis-table th,
.analysis-table td {
    text-align: left;
    padding: 10px;
    border-bottom: 1px solid #ddd;
}

.analysis-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #333;
}

.analysis-table tr:hover {
    background-color: #f8f9fa;
}

/* Error Messages */
.error-message {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 4px;
    padding: 15px;
    color: #856404;
    margin-top: 10px;
}

.error-message.info {
    background-color: #d1ecf1;
    border-color: #0c5460;
    color: #0c5460;
}
```

**Acceptance Criteria:**
- [ ] Tab styles added
- [ ] Loading spinner styled
- [ ] Analysis display styles added
- [ ] Responsive design maintained
- [ ] Consistent with existing styles

---

### Task 3.3: Implement JavaScript State Management
**Priority:** CRITICAL  
**Depends On:** Task 3.1  
**Estimated Time:** 1 hour

**File:** `static/app.js`

**Add State Object:**
```javascript
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
```

**Acceptance Criteria:**
- [ ] State object created
- [ ] State management functions implemented
- [ ] Clear state structure
- [ ] Helper functions for state queries

---

### Task 3.4: Implement Tab Switching Logic
**Priority:** CRITICAL  
**Depends On:** Task 3.3  
**Estimated Time:** 45 minutes

**File:** `static/app.js`

**Implementation:**
```javascript
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

// Initialize tabs on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
});
```

**Acceptance Criteria:**
- [ ] Tab switching works smoothly
- [ ] Active tab highlighted
- [ ] Content visibility toggled correctly
- [ ] Analysis lazy-loaded on first tab click
- [ ] Cached analysis displayed on subsequent clicks

---

### Task 3.5: Implement Analysis API Call
**Priority:** CRITICAL  
**Depends On:** Task 3.4, Backend Task 2.2  
**Estimated Time:** 1 hour

**File:** `static/app.js`

**Implementation:**
```javascript
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
```

**Acceptance Criteria:**
- [ ] Fetch function implemented
- [ ] Loading states handled
- [ ] Error handling comprehensive
- [ ] Success/error/too_large responses handled
- [ ] User feedback at all stages

---

### Task 3.6: Implement Analysis Rendering
**Priority:** CRITICAL  
**Depends On:** Task 3.5  
**Estimated Time:** 1.5 hours

**File:** `static/app.js`

**Implementation:**
```javascript
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
```

**Acceptance Criteria:**
- [ ] Rendering functions for all 4 statistics sections
- [ ] Dataset overview displayed
- [ ] Variable types formatted as cards
- [ ] Numeric stats in table format
- [ ] Cardinality with uniqueness percentage
- [ ] Missing values with visual indicators
- [ ] Responsive tables with horizontal scroll
- [ ] Number formatting helpers

---

### Task 3.7: Integrate with Existing Query Flow
**Priority:** CRITICAL  
**Depends On:** Task 3.6  
**Estimated Time:** 30 minutes

**File:** `static/app.js`

**Actions:**

Find the existing `handleQuery` or similar function and update:

```javascript
// Modify existing query success handler
async function handleQuerySuccess(data) {
    // Existing code for displaying SQL and results...
    document.getElementById("sql-query-output").textContent = data.sql || "No SQL generated.";
    
    // Store results in state
    appState.currentQuery.results = {
        columns: data.columns || [],
        rows: data.rows || []
    };
    appState.currentQuery.sql = data.sql;
    appState.currentQuery.timestamp = Date.now();
    
    // Reset analysis state for new query
    resetAnalysisState();
    
    // Display results in Results tab
    displayResults(data.columns, data.rows);
    
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

function displayResults(columns, rows) {
    const resultsDiv = document.getElementById('results-output');
    
    if (!rows || rows.length === 0) {
        resultsDiv.innerHTML = '<p>No results found.</p>';
        return;
    }
    
    // Existing result table rendering code...
    // (Keep existing implementation)
}
```

**Acceptance Criteria:**
- [ ] Query results stored in state
- [ ] Analysis state reset on new query
- [ ] Analysis tab enabled/disabled based on row count
- [ ] Results tab active by default
- [ ] Smooth integration with existing code

---

## Phase 4: Testing & Documentation (2-3 hours)

### Task 4.1: Manual End-to-End Testing
**Priority:** HIGH  
**Depends On:** All frontend tasks  
**Estimated Time:** 1 hour

**Test Scenarios:**

1. **Happy Path:**
   - [ ] Submit query returning 100 rows
   - [ ] Verify Results tab displays data
   - [ ] Click Analysis tab
   - [ ] Verify loading indicator appears
   - [ ] Verify analysis displays correctly
   - [ ] Switch back to Results tab
   - [ ] Switch to Analysis again (verify cached)

2. **Large Dataset:**
   - [ ] Submit query returning > 50,000 rows
   - [ ] Click Analysis tab
   - [ ] Verify "too large" message displayed

3. **Small Dataset:**
   - [ ] Submit query returning 1 row
   - [ ] Verify Analysis tab is disabled
   - [ ] Verify tooltip shows "requires at least 2 rows"

4. **Empty Results:**
   - [ ] Submit query with no results
   - [ ] Verify Analysis tab disabled

5. **Mixed Data Types:**
   - [ ] Query with numeric, text, and date columns
   - [ ] Verify variable types correctly categorized
   - [ ] Verify statistics appear for numeric columns only

6. **Null Values:**
   - [ ] Query with null values
   - [ ] Verify missing values section highlights nulls

7. **Multiple Queries:**
   - [ ] Run query 1, view analysis
   - [ ] Run query 2
   - [ ] Verify analysis cleared
   - [ ] View query 2 analysis
   - [ ] Verify new analysis displayed

8. **Error Handling:**
   - [ ] Simulate backend error (stop server mid-analysis)
   - [ ] Verify error message displayed
   - [ ] Verify Results tab still functional

**Test Data Queries:**
```sql
-- Happy path (100 rows)
SELECT TOP 100 ProductID, Name, ListPrice 
FROM Production.Product;

-- Large dataset (simulate, adjust limit)
SELECT * FROM Sales.SalesOrderDetail;

-- Single row
SELECT TOP 1 * FROM Production.Product;

-- With nulls
SELECT ProductID, Name, Weight, Color 
FROM Production.Product;

-- Mixed types
SELECT ProductID, Name, ListPrice, ModifiedDate 
FROM Production.Product;
```

**Acceptance Criteria:**
- [ ] All 8 test scenarios pass
- [ ] No console errors
- [ ] UI responsive and smooth
- [ ] Error messages user-friendly

---

### Task 4.2: Update README Documentation
**Priority:** MEDIUM  
**Depends On:** Task 4.1  
**Estimated Time:** 30 minutes

**File:** `README.md`

**Add Section:**
```markdown
## Analysis Feature

### Overview
The SQL Chatbot now includes automatic data analysis capabilities. After executing a query, users can view statistical insights about their data in the Analysis tab.

### Features
- **Variable Type Summary:** Breakdown of column data types
- **Numeric Statistics:** Mean, standard deviation, quartiles for numeric columns
- **Cardinality Analysis:** Unique value counts for all columns
- **Missing Values:** Detection of null/missing data

### Usage
1. Submit a natural language question
2. View query results in the Results tab
3. Click the **Analysis** tab to see statistical summary
4. Analysis is generated automatically (< 2 seconds for typical datasets)

### Limitations
- Analysis requires at least 2 rows of data
- Maximum dataset size: 50,000 rows
- Datasets exceeding the limit will display an informational message

### Dependencies
- `skimpy==0.0.9` - Statistical analysis engine
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical operations
```

**Acceptance Criteria:**
- [ ] README updated with Analysis section
- [ ] Features documented
- [ ] Usage instructions clear
- [ ] Limitations stated
- [ ] Dependencies listed

---

### Task 4.3: Update API Documentation
**Priority:** MEDIUM  
**Depends On:** None  
**Estimated Time:** 30 minutes

**Create/Update:** `docs/api.md` or add to README

**Add Endpoint Documentation:**
```markdown
## API Endpoints

### POST /api/analyze

Generate statistical analysis for query results.

**Request Body:**
```json
{
  "columns": ["string"],
  "rows": [{"column": "value"}]
}
```

**Response (Success):**
```json
{
  "status": "success",
  "row_count": 150,
  "column_count": 5,
  "variable_types": {
    "numeric": 2,
    "categorical": 2,
    "datetime": 1
  },
  "numeric_stats": [...],
  "cardinality": [...],
  "missing_values": [...]
}
```

**Response (Too Large):**
```json
{
  "status": "too_large",
  "row_count": 75000,
  "message": "Analysis unavailable for datasets exceeding 50,000 rows..."
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Analysis could not be generated...",
  "error_detail": "..."
}
```

**Status Codes:**
- 200: Success (includes all response types above)
- 422: Validation error (malformed request)
- 500: Server error
```

**Acceptance Criteria:**
- [ ] Endpoint documented
- [ ] Request format specified
- [ ] All response types documented
- [ ] Status codes listed

---

## Phase 5: Deployment Checklist (1 hour)

### Task 5.1: Pre-Deployment Verification
**Priority:** CRITICAL  
**Estimated Time:** 30 minutes

**Checklist:**
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Manual testing completed
- [ ] No console errors in browser
- [ ] No Python warnings/errors in logs
- [ ] README updated
- [ ] API documentation complete
- [ ] Code reviewed (if applicable)
- [ ] Git branch up to date

**Commands:**
```bash
# Run all tests
pytest tests/ -v

# Check code coverage
pytest tests/ --cov=app

# Lint Python code
flake8 app/ tests/

# Start server and verify
python -m uvicorn app.main:app --reload
```

---

### Task 5.2: Deployment Steps
**Priority:** CRITICAL  
**Estimated Time:** 30 minutes

**Steps:**

1. **Update requirements.txt:**
```bash
pip freeze > requirements.txt
```

2. **Commit changes:**
```bash
git add .
git commit -m "feat: Add automatic data analysis feature with skimpy

- Add /api/analyze endpoint for statistical analysis
- Implement tab interface for Results and Analysis
- Add comprehensive test suite
- Update documentation

Closes #[issue-number]"
```

3. **Push to repository:**
```bash
git push origin feature/analysis-feature
```

4. **Create pull request** (if using PR workflow)

5. **Deploy to production:**
```bash
# Depends on your deployment process
# Example for simple deployment:
pip install -r requirements.txt
systemctl restart sql-chatbot  # or your service name
```

6. **Verify deployment:**
- [ ] Access application URL
- [ ] Test query execution
- [ ] Test analysis generation
- [ ] Check logs for errors

---

## Summary

### Total Effort Breakdown

| Phase | Tasks | Estimated Time |
|:------|:------|:---------------|
| Phase 1: Setup | 2 | 0.5 hours |
| Phase 2: Backend | 4 | 4-6 hours |
| Phase 3: Frontend | 7 | 4-5 hours |
| Phase 4: Testing & Docs | 3 | 2-3 hours |
| Phase 5: Deployment | 2 | 1 hour |
| **Total** | **18 tasks** | **12-16 hours (2-3 days)** |

### Critical Path

```
Setup (0.5h)
    ↓
Backend Service (2h)
    ↓
Backend Endpoint (0.5h)
    ↓
Backend Tests (2.5h)
    ↓
Frontend HTML (0.5h) ← Can run parallel to backend
    ↓
Frontend CSS (0.5h)
    ↓
Frontend State (1h)
    ↓
Frontend Tabs (0.75h)
    ↓
Frontend API Call (1h)
    ↓
Frontend Rendering (1.5h)
    ↓
Integration (0.5h)
    ↓
Testing (1h)
    ↓
Documentation (1h)
    ↓
Deployment (1h)
```

### Risk Mitigation

| Risk | Mitigation |
|:-----|:-----------|
| Skimpy compatibility issues | Test thoroughly in Phase 1, have pandas fallback |
| Frontend state bugs | Comprehensive state management in Task 3.3 |
| Performance with large datasets | 50K row limit + caching strategy |
| Integration issues | Clear acceptance criteria for each task |

---

## Quick Start for Developers

```bash
# 1. Install dependencies
pip install skimpy==0.0.9 pandas>=2.0.0 numpy>=1.24.0

# 2. Create analysis service
# Implement app/analysis_service.py (see Task 2.1)

# 3. Add endpoint
# Update app/main.py (see Task 2.2)

# 4. Update frontend
# Modify static/index.html (see Task 3.1)
# Modify static/styles.css (see Task 3.2)
# Modify static/app.js (see Tasks 3.3-3.7)

# 5. Test
pytest tests/ -v

# 6. Run
python -m uvicorn app.main:app --reload

# 7. Verify
# Open browser to http://localhost:8000
# Submit query, click Analysis tab
```

---

**Document Created By:** Cline (Quality Gate Validator)  
**Based On:** Architecture Document v1.0  
**Status:** Ready for Implementation  
**Next Action:** Begin Phase 1 - Setup & Dependencies
