# Story 004: Visualization Sandbox Skeleton

**Epic:** E3 - Visualization Sandbox Epic  
**Priority:** P1  
**Labels:** `epic:E3`, `type:story`, `prio:P1`, `security`  
**Status:** Ready for Review

## Context

Create a secure, sandboxed visualization renderer using matplotlib/seaborn with strict security constraints. This component must generate charts from SQL result data without any filesystem or network access, operating within strict CPU/RAM/time limits to prevent resource abuse.

The sandbox must be completely isolated and headless, returning PNG images with captions for safe consumption by the UI layer. This is a **prerequisite** for the UI (E4) to render charts.

## Story

**As a** user of the SQL Chatbot application  
**I want** to generate secure visualizations from my SQL query results  
**So that** I can better understand my data through charts and graphs without compromising system security

## Tasks

### Sandboxed Environment Setup
- [x] Configure matplotlib with Agg (non-GUI) backend for headless operation
- [x] Set up seaborn integration for enhanced statistical visualizations
- [x] Implement import whitelist (matplotlib, seaborn, numpy, pandas only)
- [x] Block all filesystem access (no file I/O operations)
- [x] Block all network access (no HTTP requests or external connections)

### Resource Limits & Security
- [x] Implement CPU time limits (max 10 seconds per render)
- [x] Enforce RAM limits (max 512MB per render process)
- [x] Set maximum image dimensions (2048x2048 pixels)
- [x] Prevent infinite loops and recursive operations
- [x] Sanitize all input data for malicious content

### Chart Generation Engine
- [x] Auto-detect appropriate chart types based on data structure
- [x] Support common chart types: bar, line, scatter, histogram, heatmap
- [x] Handle categorical vs numerical data appropriately
- [x] Generate meaningful chart titles and axis labels
- [x] Apply consistent styling and color schemes

### Output & Metadata
- [x] Generate PNG format images with proper compression
- [x] Create descriptive captions explaining the visualization
- [x] Return base64-encoded image data for API consumption
- [x] Include chart metadata (type, dimensions, data summary)
- [x] Handle errors gracefully with fallback visualizations

### Integration Points
- [x] Accept structured data from SQL execution results
- [x] Provide clear API interface for chart generation requests
- [x] Handle various SQL result formats (single column, multiple columns, aggregated data)
- [x] Support data preprocessing for visualization optimization

## Acceptance Criteria

1. **Headless Operation:** Renders charts without GUI dependencies using matplotlib Agg backend
2. **Security Isolation:** No filesystem or network access; only whitelisted imports allowed
3. **Resource Limits:** CPU (10s), RAM (512MB), and image size (2048x2048) limits enforced
4. **Chart Generation:** Auto-detects appropriate chart types and generates meaningful visualizations
5. **PNG Output:** Returns base64-encoded PNG images with descriptive captions
6. **Error Handling:** Gracefully handles invalid data with fallback responses
7. **CI Compatibility:** Renders successfully in headless CI environment
8. **Performance:** Typical charts render within 3 seconds

## Definition of Done

- [ ] Tests green locally and in CI; minimal coverage on new code
- [ ] CI renders PNG headlessly; sandbox limits verified
- [ ] Config/docs updated (`.env.example`, `README_dev.md`)  
- [ ] Logs include correlation IDs; errors are user-safe (no secrets, no stack dumps)
- [ ] Security: sandbox limits verified and tested
- [ ] Performance: benchmark tests for typical chart rendering
- [ ] Documentation includes supported chart types and data formats

## Dev Notes

### Technical Requirements
- matplotlib with Agg backend (no GUI dependencies)
- seaborn for statistical visualizations
- Strict import whitelist enforcement
- Resource monitoring and limits
- Base64 encoding for image transport

### Chart Type Detection Logic
```python
def detect_chart_type(data):
    if len(data.columns) == 1:
        if data.dtypes[0] in ['object', 'category']:
            return 'bar'  # Categorical counts
        else:
            return 'histogram'  # Numerical distribution
    elif len(data.columns) == 2:
        if both_numeric(data):
            return 'scatter'  # Numeric vs numeric
        else:
            return 'bar'  # Category vs numeric
    else:
        return 'correlation_heatmap'  # Multiple columns
```

### Security Configuration
```python
# Whitelist only safe imports
ALLOWED_IMPORTS = [
    'matplotlib', 'matplotlib.pyplot', 'seaborn', 
    'numpy', 'pandas', 'io', 'base64'
]

# Resource limits
MAX_CPU_TIME = 10  # seconds
MAX_MEMORY = 512 * 1024 * 1024  # 512MB
MAX_IMAGE_SIZE = (2048, 2048)
```

### Output Format
```json
{
  "success": true,
  "image_data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "image_format": "png",
  "caption": "Bar chart showing product sales by category",
  "chart_type": "bar",
  "dimensions": [800, 600],
  "data_summary": {
    "rows": 10,
    "columns": 2,
    "chart_title": "Product Sales by Category"
  }
}
```

## Testing

### Unit Tests Required
- Chart type detection logic with various data structures
- Import whitelist enforcement blocks unauthorized modules
- Resource limits prevent CPU/memory exhaustion
- PNG generation and base64 encoding
- Error handling for malformed data
- Fallback chart generation for edge cases

### Security Tests Required
- Filesystem access prevention (no file operations)
- Network access prevention (no HTTP requests)
- Resource limit enforcement (CPU timeout, memory limits)
- Import restriction bypass attempts
- Malicious data input handling

### Integration Tests Required
- End-to-end chart generation from SQL results
- CI headless rendering verification
- Performance benchmarks for various chart types
- Error recovery and fallback behavior

### Test Data
```python
# Various data structures to test chart detection
test_cases = [
    # Single categorical column
    pd.DataFrame({'Category': ['A', 'B', 'C', 'A', 'B']}),
    
    # Single numerical column  
    pd.DataFrame({'Sales': [100, 200, 150, 300, 250]}),
    
    # Two numerical columns
    pd.DataFrame({'Sales': [100, 200, 150], 'Profit': [20, 40, 30]}),
    
    # Mixed categorical and numerical
    pd.DataFrame({'Category': ['A', 'B', 'C'], 'Sales': [100, 200, 150]})
]
```

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Tasks Completed
- [ ] Sandboxed environment setup (matplotlib Agg, seaborn)
- [ ] Resource limits and security constraints
- [ ] Chart generation engine
- [ ] Output format and metadata
- [ ] Integration API design
- [ ] Unit tests for chart generation
- [ ] Security tests for sandbox isolation
- [ ] CI headless rendering verification

### Debug Log References
_To be filled by dev agent with links to specific debug sessions_

### Completion Notes
_To be filled by dev agent with implementation details and decisions_

### File List
_To be filled by dev agent with all new/modified/deleted files_

### Change Log
_To be filled by dev agent with detailed changes made_
