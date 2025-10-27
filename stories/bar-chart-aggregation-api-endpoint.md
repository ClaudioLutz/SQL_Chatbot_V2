# User Story: Bar Chart Aggregation API Endpoint Integration

**Story ID:** BCA-002  
**Epic:** Bar Chart Aggregation Feature  
**Status:** Complete  
**Priority:** Must Have  
**Estimated Effort:** 1 hour  
**Dependencies:** BCA-001 (Backend Service)

---

## Story

**As a** backend developer  
**I want** to integrate bar chart aggregation into the visualization API endpoint  
**So that** frontend requests automatically receive aggregated data for bar charts

---

## Acceptance Criteria

- [ ] `/api/visualize` endpoint updated in `app/main.py`
- [ ] Conditional logic added to detect bar chart type
- [ ] Calls `prepare_bar_chart_data()` for bar chart requests
- [ ] Returns aggregated rows (50 max) instead of raw data (1M+)
- [ ] Response includes metadata (aggregation method, rows aggregated, categories shown)
- [ ] Error handling for aggregation failures (e.g., empty data)
- [ ] Logging statements for observability
- [ ] Backward compatibility maintained for other chart types (scatter, line, histogram)
- [ ] Response time <100ms for API processing (excluding aggregation)
- [ ] Integration tests pass

---

## Technical Implementation

### File: `app/main.py`

```python
from app.visualization_service import (
    prepare_visualization_data,
    prepare_bar_chart_data  # NEW IMPORT
)

@app.post("/api/visualize")
async def visualize(request: VisualizationRequest):
    """
    Generate visualization data with automatic aggregation for bar charts.
    
    For bar charts, automatically aggregates duplicate categories.
    For other chart types, uses existing sampling logic.
    """
    try:
        df = pd.DataFrame(request.rows)
        
        if request.chartType == "bar":
            # ===== NEW: Bar Chart Aggregation =====
            logger.info(
                f"Generating bar chart: X={request.xColumn}, "
                f"Y={request.yColumn or 'None'}"
            )
            
            # Aggregate data on backend
            chart_data = prepare_bar_chart_data(
                df=df,
                x_column=request.xColumn,
                y_column=request.yColumn,
                aggregation="auto",  # Smart detection
                max_categories=50
            )
            
            # Format response for frontend
            aggregated_rows = [
                {
                    request.xColumn: cat,
                    'value': val
                }
                for cat, val in zip(
                    chart_data['categories'], 
                    chart_data['values']
                )
            ]
            
            logger.info(
                f"Bar chart aggregated: {chart_data['rows_aggregated']} rows → "
                f"{chart_data['categories_shown']} categories "
                f"(method: {chart_data['aggregation']})"
            )
            
            return {
                "status": "success",
                "data": {
                    "columns": [request.xColumn, "value"],
                    "rows": aggregated_rows
                },
                "metadata": chart_data,
                "is_sampled": False,  # Already aggregated, not sampled
                "column_types": {
                    request.xColumn: "categorical",
                    "value": "numeric"
                }
            }
        
        else:
            # ===== EXISTING: Other chart types =====
            return prepare_visualization_data(
                df=df,
                chart_type=request.chartType,
                x_column=request.xColumn,
                y_column=request.yColumn,
                max_rows=request.maxRows
            )
    
    except Exception as e:
        logger.error(
            f"Visualization error: {str(e)}", 
            exc_info=True
        )
        return {
            "status": "error",
            "message": str(e)
        }
```

### Error Handling Examples

```python
# Handle empty dataframe
if len(df) == 0:
    return {
        "status": "error",
        "message": "No data available for visualization"
    }

# Handle missing columns
if request.xColumn not in df.columns:
    return {
        "status": "error",
        "message": f"Column '{request.xColumn}' not found in results"
    }

# Handle non-categorical X column (if validation needed)
if df[request.xColumn].nunique() > 1000:
    logger.warning(
        f"X-column has {df[request.xColumn].nunique()} unique values. "
        f"Limiting to top 50."
    )
```

---

## API Response Format

### Success Response Example

```json
{
  "status": "success",
  "data": {
    "columns": ["Status", "value"],
    "rows": [
      {"Status": "Active", "value": 523891.50},
      {"Status": "Pending", "value": 234567.25},
      {"Status": "Completed", "value": 187432.80},
      {"Status": "Cancelled", "value": 45678.15}
    ]
  },
  "metadata": {
    "categories": ["Active", "Pending", "Completed", "Cancelled"],
    "values": [523891.50, 234567.25, 187432.80, 45678.15],
    "chart_title": "Total Amount by Status",
    "y_axis_label": "Total Amount",
    "x_axis_label": "Status",
    "aggregation": "sum",
    "rows_aggregated": 1000000,
    "categories_shown": 4,
    "total_categories": 4,
    "value_column": "Amount"
  },
  "is_sampled": false,
  "column_types": {
    "Status": "categorical",
    "value": "numeric"
  }
}
```

### Error Response Example

```json
{
  "status": "error",
  "message": "Insufficient data after removing missing values. At least 2 complete rows required."
}
```

---

## Testing Requirements

### Integration Tests (`tests/test_visualize_endpoint.py`)

1. **test_visualize_bar_chart_count_aggregation**
   - POST to `/api/visualize` with chartType="bar", xColumn only
   - Assert: status="success"
   - Assert: Returns aggregated data with COUNT
   - Assert: metadata includes aggregation info

2. **test_visualize_bar_chart_sum_aggregation**
   - POST with chartType="bar", xColumn + numeric yColumn
   - Assert: Returns aggregated data with SUM
   - Assert: metadata.aggregation="sum"

3. **test_visualize_bar_chart_large_dataset**
   - POST with 1M rows, 8 unique categories
   - Assert: Returns only 8 rows (aggregated)
   - Assert: metadata.rows_aggregated=1000000
   - Assert: Response time <1 second

4. **test_visualize_bar_chart_many_categories**
   - POST with 150 unique categories
   - Assert: Returns top 50 only
   - Assert: metadata.categories_shown=50
   - Assert: metadata.total_categories=150

5. **test_visualize_bar_chart_error_empty_data**
   - POST with empty rows array
   - Assert: status="error"
   - Assert: Error message indicates no data

6. **test_visualize_scatter_unchanged**
   - POST with chartType="scatter"
   - Assert: Uses existing logic (not aggregation path)
   - Assert: Backward compatibility maintained

7. **test_visualize_histogram_unchanged**
   - POST with chartType="histogram"
   - Assert: Uses existing logic
   - Assert: Bins parameter still works

---

## Logging Strategy

### Key Logging Points

```python
# Request received
logger.info(
    f"Visualization request: type={request.chartType}, "
    f"rows={len(df)}, x={request.xColumn}, y={request.yColumn}"
)

# Aggregation started (bar charts only)
logger.info(f"Starting bar chart aggregation for {len(df)} rows")

# Aggregation completed
logger.info(
    f"Bar chart aggregated: {original_rows} rows → "
    f"{aggregated_rows} categories in {elapsed_ms}ms"
)

# Top 50 limiting applied
logger.warning(
    f"Limited to top 50 of {total_categories} categories "
    f"for X-column '{x_column}'"
)

# Error occurred
logger.error(
    f"Aggregation failed: {error_message}", 
    exc_info=True
)
```

---

## Performance Requirements

### API Response Time Targets

| Operation | Target Time | Measured At |
|:----------|:------------|:------------|
| Request parsing | <10ms | FastAPI handler |
| Aggregation (1M rows) | <500ms | Backend function |
| Response formatting | <50ms | JSON serialization |
| **Total API time** | **<600ms** | End-to-end |

### Network Transfer Savings

| Scenario | Before | After | Savings |
|:---------|:-------|:------|:--------|
| 1M rows, 8 categories | 1M rows (~50MB) | 8 rows (~1KB) | 99.998% |
| 100K rows, 20 categories | 100K rows (~5MB) | 20 rows (~2KB) | 99.96% |

---

## Backward Compatibility

### Unchanged Chart Types

**These chart types should work exactly as before:**

- **Scatter plots** - Use existing `prepare_visualization_data()`
- **Line charts** - Use existing logic
- **Histograms** - Use existing logic with bins parameter
- **Any future chart types** - Default to existing behavior

### Verification Checklist

- [ ] Scatter plot still samples large datasets correctly
- [ ] Histogram bins parameter still works
- [ ] Line chart rendering unchanged
- [ ] Error messages consistent across all chart types
- [ ] Response format consistent (same structure)

---

## Dependencies

- BCA-001: Backend aggregation service must be complete
- Existing `prepare_visualization_data()` function
- FastAPI request/response models
- pandas DataFrame handling

---

## Edge Cases to Handle

1. **No rows in DataFrame** - Return error immediately
2. **Missing X-column** - Return error before aggregation
3. **Missing Y-column when specified** - Fall back to COUNT
4. **All NULL X-column values** - Return error after cleaning
5. **Very long processing (>5s)** - Log warning, continue
6. **Invalid aggregation method** - Caught by backend, return error
7. **Empty result after aggregation** - Return error

---

## Rollback Plan

### If Issues Arise

```python
# Quick rollback: Add feature flag
ENABLE_BAR_CHART_AGGREGATION = os.getenv(
    "ENABLE_BAR_CHART_AGGREGATION", 
    "true"
) == "true"

if request.chartType == "bar" and ENABLE_BAR_CHART_AGGREGATION:
    # Use new aggregation path
    chart_data = prepare_bar_chart_data(...)
else:
    # Fall back to old behavior
    return prepare_visualization_data(...)
```

---

## Definition of Done

- [ ] Code implemented in `app/main.py`
- [ ] Conditional logic for bar charts works correctly
- [ ] All 7 integration tests written and passing
- [ ] Error handling comprehensive
- [ ] Logging statements added for observability
- [ ] Response format matches specification
- [ ] Backward compatibility verified for all chart types
- [ ] Performance targets met (<600ms total)
- [ ] Code reviewed by tech lead
- [ ] No linting errors

---

## Notes

- Minimal changes to existing endpoint structure
- Bar chart logic isolated in conditional block
- Easy to extend for other chart types if needed
- Metadata provides transparency for frontend
- Error messages are user-friendly and actionable
