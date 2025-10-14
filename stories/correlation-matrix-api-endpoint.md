# User Story: Correlation Matrix API Endpoint

**Story ID:** CM-002  
**Epic:** Correlation Matrix Feature  
**Status:** Draft  
**Priority:** High  
**Estimated Effort:** 0.5 day  
**Depends On:** CM-001 (Backend Service)

---

## Story

**As a** frontend developer  
**I want** a REST API endpoint to calculate correlation matrices  
**So that** the frontend can request correlations for large datasets

---

## Acceptance Criteria

- [ ] POST endpoint `/api/correlation-matrix` created in `app/main.py`
- [ ] Accepts JSON payload with columns, rows, and maxRows
- [ ] Uses `CorrelationMatrixRequest` Pydantic model for validation
- [ ] Validates 2-15 column range at API level
- [ ] Calls `calculate_correlation_matrix()` service function
- [ ] Returns correlation matrix data as JSON
- [ ] Returns HTTP 200 on success
- [ ] Returns HTTP 422 for validation errors
- [ ] Returns HTTP 500 for server errors
- [ ] Includes processing time in response
- [ ] Includes performance warning for large datasets without sampling
- [ ] Endpoint completes in <3 seconds for 50K rows

---

## Technical Implementation

### Pydantic Request Model

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CorrelationMatrixRequest(BaseModel):
    columns: List[str] = Field(..., min_items=2, max_items=15)
    rows: List[Dict[str, Any]]
    maxRows: Optional[int] = Field(10000, ge=100)
```

### API Endpoint

```python
@app.post("/api/correlation-matrix")
async def correlation_matrix_endpoint(request: CorrelationMatrixRequest):
    """
    Calculate correlation matrix for selected numeric columns.
    
    NO ROW LIMITS - Users can process datasets of ANY size.
    Sampling is RECOMMENDED for performance, not required.
    
    Request:
        - columns: List[str] - Column names (2-15)
        - rows: List[dict] - Query result data
        - maxRows: Optional[int] - Max rows before sampling (default 10000)
    
    Response:
        - status: "success" | "error" | "warning"
        - correlation_matrix: Dict[str, Dict[str, float]]
        - columns: List[str]
        - is_sampled: bool
        - sample_size: int
        - original_size: int
        - rows_with_missing_data: int
        - processing_time: float
        - warning: Optional[str]
    """
    import time
    start_time = time.time()
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.rows)
        
        # Validate request
        validation = validate_correlation_request(df, request.columns)
        if not validation["valid"]:
            return {
                "status": "error",
                "message": validation["message"]
            }
        
        # Warn for large datasets without sampling
        warning = None
        if len(df) > 100000 and (request.maxRows is None or request.maxRows >= len(df)):
            warning = (
                f"Processing {len(df):,} rows without sampling. "
                f"This may take 10-30 seconds. Consider setting maxRows "
                f"to 10000-100000 for faster results."
            )
            logger.info(f"Large dataset correlation: {len(df)} rows, {len(request.columns)} columns")
        
        # Calculate correlation matrix
        result = calculate_correlation_matrix(
            df=df,
            columns=request.columns,
            max_rows=request.maxRows if request.maxRows else len(df)
        )
        
        # Add metadata
        result["processing_time"] = round(time.time() - start_time, 2)
        if warning:
            result["warning"] = warning
        
        return result
        
    except ValueError as e:
        # Validation errors
        logger.warning(f"Correlation matrix validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "error_type": "validation"
        }
    except Exception as e:
        # Unexpected errors
        logger.error(f"Correlation matrix error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Failed to calculate correlation matrix. Please try again.",
            "error_type": "server"
        }
```

---

## Testing Requirements

### Integration Tests (`tests/test_correlation_endpoint.py`)

1. **test_correlation_matrix_endpoint_success**
   - POST valid request with 2 numeric columns
   - Assert: HTTP 200, status="success", correlation_matrix returned

2. **test_correlation_matrix_endpoint_large_dataset**
   - POST request with 50K rows, maxRows=10000
   - Assert: is_sampled=True, sample_size=10000

3. **test_correlation_matrix_endpoint_too_few_columns**
   - POST request with 1 column
   - Assert: HTTP 422 Pydantic validation error

4. **test_correlation_matrix_endpoint_too_many_columns**
   - POST request with 16 columns
   - Assert: HTTP 422 Pydantic validation error

5. **test_correlation_matrix_endpoint_non_numeric_columns**
   - POST request with mix of numeric and text columns
   - Assert: HTTP 200, status="error", validation message

6. **test_correlation_matrix_endpoint_missing_data**
   - POST request with NaN values
   - Assert: rows_with_missing_data count in response

7. **test_correlation_matrix_endpoint_insufficient_data**
   - POST request with all NaN values (no complete rows)
   - Assert: status="error", message about insufficient data

---

## API Documentation

### Request Example

```json
{
  "columns": ["UnitPrice", "Quantity", "Discount", "TotalSales"],
  "rows": [
    {"UnitPrice": 10.5, "Quantity": 2, "Discount": 0.1, "TotalSales": 18.9},
    {"UnitPrice": 15.0, "Quantity": 3, "Discount": 0.0, "TotalSales": 45.0}
  ],
  "maxRows": 10000
}
```

### Success Response Example

```json
{
  "status": "success",
  "correlation_matrix": {
    "UnitPrice": {
      "UnitPrice": 1.0,
      "Quantity": 0.12,
      "Discount": -0.03,
      "TotalSales": 0.45
    },
    "Quantity": {
      "UnitPrice": 0.12,
      "Quantity": 1.0,
      "Discount": -0.72,
      "TotalSales": 0.89
    }
  },
  "columns": ["UnitPrice", "Quantity", "Discount", "TotalSales"],
  "is_sampled": false,
  "sample_size": 1000,
  "original_size": 1000,
  "rows_with_missing_data": 0,
  "processing_time": 0.23
}
```

### Error Response Example

```json
{
  "status": "error",
  "message": "At least 2 columns required for correlation matrix.",
  "error_type": "validation"
}
```

---

## Definition of Done

- [ ] Endpoint implemented in app/main.py
- [ ] Pydantic model created and validates input
- [ ] All integration tests written and passing
- [ ] Error handling covers all edge cases
- [ ] API documentation complete
- [ ] Performance benchmarks met
- [ ] Code reviewed
- [ ] No linting errors

---

## Notes

- Endpoint processes datasets of any size (no hard row limits)
- Performance warnings guide users on sampling configuration
- Consistent error response format with existing endpoints
- Processing time tracked for monitoring and optimization
