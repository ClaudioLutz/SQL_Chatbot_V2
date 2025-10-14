# User Story: Backend Correlation Matrix Service

**Story ID:** CM-001  
**Epic:** Correlation Matrix Feature  
**Status:** Draft  
**Priority:** High  
**Estimated Effort:** 1 day  

---

## Story

**As a** backend developer  
**I want** to implement the correlation matrix calculation service  
**So that** the application can compute Pearson correlations for numeric datasets of any size

---

## Acceptance Criteria

- [ ] `calculate_correlation_matrix()` function added to `app/visualization_service.py`
- [ ] Function accepts DataFrame, column list, and max_rows parameter
- [ ] Implements Pearson correlation using pandas `.corr()` method
- [ ] Handles sampling for datasets exceeding max_rows threshold
- [ ] Returns nested dictionary with correlation matrix, metadata, and sampling info
- [ ] Drops rows with NaN values before calculation
- [ ] Validates minimum 2 rows remain after NaN removal
- [ ] Returns proper error messages for insufficient data
- [ ] Function executes in <3 seconds for 50K rows, 10 columns
- [ ] All numeric type columns supported (int, float)

---

## Technical Implementation

### File: `app/visualization_service.py`

```python
def calculate_correlation_matrix(
    df: pd.DataFrame,
    columns: List[str],
    max_rows: int = 10000
) -> dict:
    """
    Calculate Pearson correlation matrix for selected numeric columns.
    
    Args:
        df: Input DataFrame
        columns: List of column names to correlate (2-15)
        max_rows: Maximum rows before sampling (default 10000)
    
    Returns:
        Dictionary with:
        - status: "success" | "error"
        - correlation_matrix: Dict[str, Dict[str, float]]
        - columns: List[str]
        - is_sampled: bool
        - sample_size: int
        - original_size: int
        - rows_with_missing_data: int
    """
    original_count = len(df)
    
    # Sample if needed
    if original_count > max_rows:
        sample_result = sample_large_dataset(df, columns[0], max_rows)
        df_sampled = sample_result["data"]
        is_sampled = True
    else:
        df_sampled = df
        is_sampled = False
    
    # Filter to selected columns and ensure numeric
    df_filtered = df_sampled[columns].select_dtypes(include=[np.number])
    
    # Validate all columns are numeric
    if len(df_filtered.columns) != len(columns):
        non_numeric = set(columns) - set(df_filtered.columns)
        raise ValueError(
            f"Non-numeric columns detected: {', '.join(non_numeric)}. "
            f"Correlation matrix requires numeric columns only."
        )
    
    # Drop rows with any NaN
    df_clean = df_filtered.dropna()
    
    if len(df_clean) < 2:
        raise ValueError(
            "Insufficient data after removing missing values. "
            "At least 2 complete rows required."
        )
    
    # Calculate correlation matrix
    corr_matrix = df_clean.corr()
    
    # Convert to nested dict
    corr_dict = {}
    for col1 in columns:
        corr_dict[col1] = {}
        for col2 in columns:
            corr_dict[col1][col2] = float(corr_matrix.loc[col1, col2])
    
    return {
        "status": "success",
        "correlation_matrix": corr_dict,
        "columns": columns,
        "is_sampled": is_sampled,
        "sample_size": len(df_clean),
        "original_size": original_count,
        "rows_with_missing_data": original_count - len(df_clean)
    }
```

### Validation Function

```python
def validate_correlation_request(
    df: pd.DataFrame,
    columns: List[str]
) -> Dict[str, bool | str]:
    """Validate correlation matrix request."""
    
    if len(columns) < 2:
        return {
            "valid": False,
            "message": "At least 2 columns required for correlation matrix."
        }
    
    if len(columns) > 15:
        return {
            "valid": False,
            "message": "Maximum 15 columns allowed for correlation matrix."
        }
    
    missing = [col for col in columns if col not in df.columns]
    if missing:
        return {
            "valid": False,
            "message": f"Columns not found: {', '.join(missing)}"
        }
    
    non_numeric = []
    for col in columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            non_numeric.append(col)
    
    if non_numeric:
        return {
            "valid": False,
            "message": f"Non-numeric columns: {', '.join(non_numeric)}"
        }
    
    return {"valid": True}
```

---

## Testing Requirements

### Unit Tests (`tests/test_visualization_service.py`)

1. **test_calculate_correlation_matrix_success**
   - Input: 3 numeric columns with clear correlations
   - Assert: Correct correlation values (A-B: 1.0, A-C: -1.0)

2. **test_calculate_correlation_matrix_with_sampling**
   - Input: 15K rows dataset
   - Assert: is_sampled=True, sample_size=10000

3. **test_calculate_correlation_matrix_missing_data**
   - Input: Dataset with NaN values
   - Assert: rows_with_missing_data count correct

4. **test_validate_correlation_request_minimum_columns**
   - Input: Single column
   - Assert: valid=False, error message contains "at least 2"

5. **test_validate_correlation_request_non_numeric**
   - Input: Mix of numeric and text columns
   - Assert: valid=False, lists non-numeric columns

---

## Dependencies

- Existing `sample_large_dataset()` function in visualization_service.py
- pandas library (already installed)
- numpy library (already installed)

---

## Definition of Done

- [ ] Code implemented and follows existing patterns
- [ ] All unit tests written and passing
- [ ] Code reviewed
- [ ] No linting errors
- [ ] Performance benchmarks met (<3s for 50K rows)
- [ ] Error handling tested for all edge cases
- [ ] Documentation strings complete

---

## Notes

- Reuses existing sampling infrastructure for consistency
- No upper row limit - users can process any dataset size
- Sampling is recommended for performance, not required
- Client-side calculation handles small datasets (<10K rows)
