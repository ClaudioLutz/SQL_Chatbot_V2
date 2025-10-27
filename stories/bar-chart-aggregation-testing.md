# User Story: Bar Chart Aggregation Testing & Quality Assurance

**Story ID:** BCA-004  
**Epic:** Bar Chart Aggregation Feature  
**Status:** Draft  
**Priority:** Must Have  
**Estimated Effort:** 1 hour  
**Dependencies:** BCA-001, BCA-002, BCA-003 (All implementation stories)

---

## Story

**As a** QA engineer  
**I want** to comprehensively test the bar chart aggregation feature  
**So that** we ensure quality, performance, and reliability before production deployment

---

## Acceptance Criteria

- [ ] All unit tests written and passing (backend service)
- [ ] All integration tests written and passing (API endpoint)
- [ ] Manual testing completed across all test scenarios
- [ ] Performance benchmarks met (<800ms end-to-end for 1M rows)
- [ ] Edge cases validated and handled gracefully
- [ ] Browser compatibility verified (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility testing passed (WCAG 2.1 AA)
- [ ] Regression testing confirms other features unchanged
- [ ] No critical or high-priority bugs
- [ ] Test documentation complete

---

## Unit Tests

### Backend Service Tests (`tests/test_visualization_service.py`)

#### Test Suite: prepare_bar_chart_data()

```python
import pytest
import pandas as pd
import time
from app.visualization_service import prepare_bar_chart_data, detect_bar_chart_aggregation_need


class TestBarChartAggregation:
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset with duplicate categories"""
        return pd.DataFrame({
            'Status': ['Active', 'Active', 'Active', 'Pending', 'Pending', 
                      'Completed', 'Completed', 'Cancelled'],
            'Amount': [100, 200, 150, 300, 250, 400, 350, 50]
        })
    
    def test_count_aggregation_no_y_column(self, sample_data):
        """Test frequency count when Y-column is None"""
        result = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column=None,
            aggregation='auto'
        )
        
        assert result['aggregation'] == 'count'
        assert len(result['categories']) == 4  # 4 unique statuses
        assert result['chart_title'] == 'Frequency Distribution of Status'
        assert result['y_axis_label'] == 'Count'
        assert result['rows_aggregated'] == 8
        assert result['categories_shown'] == 4
        # Verify sorted by count descending
        assert result['categories'][0] == 'Active'  # 3 occurrences
        assert result['values'][0] == 3
    
    def test_sum_aggregation_with_numeric_y(self, sample_data):
        """Test SUM aggregation with numeric Y-column"""
        result = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column='Amount',
            aggregation='auto'
        )
        
        assert result['aggregation'] == 'sum'
        assert result['chart_title'] == 'Total Amount by Status'
        assert result['y_axis_label'] == 'Total Amount'
        # Verify calculations
        active_total = 100 + 200 + 150  # 450
        assert result['values'][result['categories'].index('Active')] == 450
    
    def test_avg_aggregation(self, sample_data):
        """Test AVG aggregation"""
        result = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column='Amount',
            aggregation='avg'
        )
        
        assert result['aggregation'] == 'avg'
        assert result['y_axis_label'] == 'Average Amount'
        # Active average: (100 + 200 + 150) / 3 = 150
        active_avg = result['values'][result['categories'].index('Active')]
        assert abs(active_avg - 150) < 0.01
    
    def test_min_max_aggregation(self, sample_data):
        """Test MIN and MAX aggregation"""
        result_min = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column='Amount',
            aggregation='min'
        )
        
        result_max = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column='Amount',
            aggregation='max'
        )
        
        assert result_min['aggregation'] == 'min'
        assert result_max['aggregation'] == 'max'
        
        # Active min should be 100, max should be 200
        active_idx_min = result_min['categories'].index('Active')
        active_idx_max = result_max['categories'].index('Active')
        assert result_min['values'][active_idx_min] == 100
        assert result_max['values'][active_idx_max] == 200
    
    def test_top_50_limiting(self):
        """Test that categories are limited to top 50"""
        # Create dataset with 200 unique categories
        data = pd.DataFrame({
            'Category': [f'Cat_{i}' for i in range(200) for _ in range(10)],
            'Value': [i * 10 for i in range(200) for _ in range(10)]
        })
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='Category',
            y_column='Value',
            aggregation='sum',
            max_categories=50
        )
        
        assert result['categories_shown'] == 50
        assert result['total_categories'] == 200
        # Verify sorted by value descending
        assert result['values'][0] > result['values'][1]
    
    def test_null_value_removal(self):
        """Test that NULL values are handled correctly"""
        data = pd.DataFrame({
            'Status': ['Active', None, 'Pending', 'Active', None],
            'Amount': [100, 200, 300, 150, 250]
        })
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='Status',
            y_column=None,
            aggregation='count'
        )
        
        assert len(result['categories']) == 2  # Only Active and Pending
        assert None not in result['categories']
        assert result['rows_aggregated'] == 5  # Original count
        assert result['categories_shown'] == 2  # After NULL removal
    
    def test_single_category(self):
        """Test handling of single category"""
        data = pd.DataFrame({
            'Status': ['Active'] * 1000,
            'Amount': list(range(1000))
        })
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='Status',
            y_column='Amount',
            aggregation='sum'
        )
        
        assert len(result['categories']) == 1
        assert result['categories'][0] == 'Active'
        assert result['rows_aggregated'] == 1000
        # Sum of 0 to 999
        assert result['values'][0] == sum(range(1000))
    
    def test_all_unique_categories(self):
        """Test when all categories are unique (no aggregation needed)"""
        data = pd.DataFrame({
            'ID': [f'ID_{i}' for i in range(10)],
            'Value': list(range(10))
        })
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='ID',
            y_column='Value',
            aggregation='sum'
        )
        
        assert result['categories_shown'] == 10
        assert result['total_categories'] == 10
        assert result['rows_aggregated'] == 10
        # Values should be unchanged (no aggregation occurred)
        assert sorted(result['values']) == list(range(10))
    
    def test_performance_large_dataset(self):
        """Test performance with 1M rows"""
        # Create 1M row dataset with 8 unique categories
        data = pd.DataFrame({
            'Category': [f'Cat_{i % 8}' for i in range(1000000)],
            'Value': list(range(1000000))
        })
        
        start_time = time.time()
        result = prepare_bar_chart_data(
            df=data,
            x_column='Category',
            y_column='Value',
            aggregation='sum'
        )
        elapsed = time.time() - start_time
        
        assert elapsed < 0.5  # Must complete in <500ms
        assert result['categories_shown'] == 8
        assert result['rows_aggregated'] == 1000000
    
    def test_detect_aggregation_need(self):
        """Test aggregation need detection"""
        data_with_dupes = pd.DataFrame({
            'Status': ['A', 'A', 'B', 'B']
        })
        
        data_unique = pd.DataFrame({
            'ID': ['1', '2', '3', '4']
        })
        
        result_dupes = detect_bar_chart_aggregation_need(
            df=data_with_dupes,
            x_column='Status'
        )
        
        result_unique = detect_bar_chart_aggregation_need(
            df=data_unique,
            x_column='ID'
        )
        
        assert result_dupes['needs_aggregation'] is True
        assert result_unique['needs_aggregation'] is False
        assert result_dupes['duplication_ratio'] == 2.0  # 4 rows / 2 unique
        assert result_unique['duplication_ratio'] == 1.0  # 4 rows / 4 unique
    
    def test_invalid_aggregation_method(self, sample_data):
        """Test error handling for invalid aggregation method"""
        with pytest.raises(ValueError, match="Unsupported aggregation method"):
            prepare_bar_chart_data(
                df=sample_data,
                x_column='Status',
                y_column='Amount',
                aggregation='invalid_method'
            )
```

**Expected Results:**
- [ ] All 12 tests pass
- [ ] Code coverage >95% for aggregation logic
- [ ] Performance test completes in <500ms

---

## Integration Tests

### API Endpoint Tests (`tests/test_visualize_endpoint.py`)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestVisualizeEndpoint:
    
    def test_bar_chart_count_aggregation(self):
        """Test bar chart with COUNT aggregation"""
        request_data = {
            "columns": ["Status", "Amount"],
            "rows": [
                {"Status": "Active", "Amount": 100},
                {"Status": "Active", "Amount": 200},
                {"Status": "Pending", "Amount": 300}
            ],
            "chartType": "bar",
            "xColumn": "Status",
            "yColumn": None,
            "maxRows": 10000
        }
        
        response = client.post("/api/visualize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["metadata"]["aggregation"] == "count"
        assert len(data["data"]["rows"]) == 2  # Active and Pending
        assert data["metadata"]["rows_aggregated"] == 3
    
    def test_bar_chart_sum_aggregation(self):
        """Test bar chart with SUM aggregation"""
        request_data = {
            "columns": ["Status", "Amount"],
            "rows": [
                {"Status": "Active", "Amount": 100},
                {"Status": "Active", "Amount": 200},
                {"Status": "Pending", "Amount": 300}
            ],
            "chartType": "bar",
            "xColumn": "Status",
            "yColumn": "Amount",
            "maxRows": 10000
        }
        
        response = client.post("/api/visualize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["aggregation"] == "sum"
        # Find Active row
        active_row = next(r for r in data["data"]["rows"] if r["Status"] == "Active")
        assert active_row["value"] == 300  # 100 + 200
    
    def test_bar_chart_category_limiting(self):
        """Test top 50 category limiting"""
        # Create 150 unique categories
        rows = [
            {"Category": f"Cat_{i}", "Value": i * 10}
            for i in range(150)
        ]
        
        request_data = {
            "columns": ["Category", "Value"],
            "rows": rows,
            "chartType": "bar",
            "xColumn": "Category",
            "yColumn": "Value",
            "maxRows": 10000
        }
        
        response = client.post("/api/visualize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["categories_shown"] == 50
        assert data["metadata"]["total_categories"] == 150
        assert len(data["data"]["rows"]) == 50
    
    def test_backward_compatibility_scatter(self):
        """Test that scatter plots still work"""
        request_data = {
            "columns": ["X", "Y"],
            "rows": [{"X": 1, "Y": 2}, {"X": 3, "Y": 4}],
            "chartType": "scatter",
            "xColumn": "X",
            "yColumn": "Y",
            "maxRows": 10000
        }
        
        response = client.post("/api/visualize", json=request_data)
        
        assert response.status_code == 200
        # Should use existing logic, not aggregation
        assert "metadata" not in response.json() or \
               "aggregation" not in response.json().get("metadata", {})
    
    def test_error_handling_empty_data(self):
        """Test error handling for empty dataset"""
        request_data = {
            "columns": ["Status"],
            "rows": [],
            "chartType": "bar",
            "xColumn": "Status",
            "yColumn": None,
            "maxRows": 10000
        }
        
        response = client.post("/api/visualize", json=request_data)
        
        # Should return error or handle gracefully
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "error"
```

**Expected Results:**
- [ ] All 5 integration tests pass
- [ ] Response times <1 second for all tests
- [ ] Error handling validates correctly

---

## Manual Testing Scenarios

### Scenario 1: Frequency Count (No Y-axis)

**Setup:**
```sql
SELECT Status FROM Orders WHERE OrderDate > '2024-01-01';
-- Returns 1M rows with 8 unique statuses
```

**Test Steps:**
1. Execute query
2. Navigate to Visualizations tab
3. Click "Bar Chart"
4. Select X-axis: "Status"
5. Leave Y-axis empty
6. Chart generates automatically

**Expected Results:**
- [ ] Chart title: "Frequency Distribution of Status"
- [ ] Y-axis label: "Count"
- [ ] 8 bars displayed (sorted by count, descending)
- [ ] Metadata annotation: "1,000,000 rows aggregated into 8 categories"
- [ ] Values show counts (e.g., 250,000)
- [ ] Response time <1 second

---

### Scenario 2: Sum Aggregation (With Y-axis)

**Setup:**
```sql
SELECT Status, Amount FROM Orders WHERE OrderDate > '2024-01-01';
-- Returns 1M rows
```

**Test Steps:**
1. Execute query
2. Generate bar chart
3. Select X-axis: "Status"
4. Select Y-axis: "Amount"

**Expected Results:**
- [ ] Chart title: "Total Amount by Status"
- [ ] Y-axis label: "Total Amount"
- [ ] Bars show summed amounts
- [ ] Metadata: "SUM: 1,000,000 rows → 8 categories"
- [ ] Large values formatted (e.g., "1.2M", "523.5K")
- [ ] Hover tooltips show full values with commas

---

### Scenario 3: Many Categories (150+ unique)

**Setup:**
```sql
SELECT ProductName, Sales FROM Products;
-- Returns 500K rows, 150 unique products
```

**Test Steps:**
1. Execute query
2. Generate bar chart
3. Select X-axis: "ProductName"
4. Select Y-axis: "Sales"

**Expected Results:**
- [ ] Only top 50 products displayed
- [ ] Warning at top: "⚠️ Showing top 50 of 150 categories"
- [ ] Bars sorted by sales (highest first)
- [ ] Metadata shows both counts: "categories_shown: 50, total_categories: 150"

---

### Scenario 4: Edge Cases

**Test Case 4.1: All Unique Categories**
```sql
SELECT ProductID, Price FROM Products LIMIT 10;
-- 10 rows, 10 unique IDs
```
- [ ] All 10 bars displayed
- [ ] No "aggregated" language in metadata
- [ ] Annotation: "10 unique categories displayed"

**Test Case 4.2: Single Category**
```sql
SELECT 'Test' as Category, Amount FROM Transactions;
-- 1M rows, 1 category
```
- [ ] Single bar displayed
- [ ] Shows aggregated total
- [ ] No errors or warnings

**Test Case 4.3: NULL Values**
```sql
SELECT Status, Amount FROM Orders;
-- Some Status values are NULL
```
- [ ] NULL values excluded from chart
- [ ] Categories shown = non-null count only
- [ ] No error messages

**Test Case 4.4: Zero Values**
```sql
SELECT Status, COALESCE(Amount, 0) as Amount FROM Orders;
-- Some amounts are zero
```
- [ ] Zero-value bars displayed as thin lines
- [ ] Tooltip shows "0.00"
- [ ] No categories excluded

**Test Case 4.5: Negative Values**
```sql
SELECT Status, Profit FROM Orders;
-- Some profits are negative
```
- [ ] Bars extend below zero line
- [ ] Y-axis includes zero with grid line
- [ ] Negative values formatted correctly

---

## Performance Testing

### Performance Benchmarks

| Dataset Size | Categories | Target Time | Test Result |
|:-------------|:-----------|:------------|:------------|
| 1K rows | 10 | <100ms | ⏱️ |
| 10K rows | 20 | <200ms | ⏱️ |
| 100K rows | 50 | <400ms | ⏱️ |
| 1M rows | 50 | <800ms | ⏱️ |
| 10M rows | 50 | <3s | ⏱️ |

**Testing Method:**
1. Generate test datasets of specified sizes
2. Execute bar chart aggregation
3. Measure end-to-end time (query → backend → frontend → render)
4. Record results in table above

**Pass Criteria:**
- [ ] All tests meet or exceed target times
- [ ] No performance regression vs. baseline
- [ ] Memory usage <500MB for 10M rows

---

## Browser Compatibility Testing

### Test Matrix

| Browser | Version | Frequency Count | Sum Aggregation | Visual Polish | Status |
|:--------|:--------|:----------------|:----------------|:--------------|:-------|
| Chrome | 120+ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Firefox | 121+ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Safari | 17+ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Edge | 120+ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |

**Test Steps for Each Browser:**
1. Load application
2. Execute test queries
3. Generate bar charts
4. Verify visual appearance
5. Test interactions (hover, resize)
6. Check console for errors

---

## Accessibility Testing

### WCAG 2.1 AA Compliance

**Test Checklist:**
- [ ] Screen reader announces chart type and data
- [ ] ARIA labels present on chart container
- [ ] Metadata readable by screen reader
- [ ] Keyboard navigation works (Tab, Arrow keys)
- [ ] Focus indicators visible
- [ ] Color contrast meets 4.5:1 minimum
- [ ] Text resizable to 200% without loss of functionality
- [ ] No flashing or blinking content

**Tools:**
- axe DevTools for automated checks
- NVDA/JAWS for screen reader testing
- Browser zoom for text scaling
- Color contrast analyzer

---

## Regression Testing

### Verify Unchanged Functionality

**Chart Types:**
- [ ] Scatter plot: Renders correctly, sampling works
- [ ] Line chart: Renders correctly
- [ ] Histogram: Renders correctly, bins parameter works

**Other Features:**
- [ ] Query execution unchanged
- [ ] Results table display unchanged
- [ ] Analysis features unchanged
- [ ] Tab switching smooth
- [ ] Error handling consistent

---

## Bug Tracking

### Bug Severity Levels

**Critical (P0):**
- Application crashes
- Data corruption
- Security vulnerabilities

**High (P1):**
- Feature doesn't work
- Performance >2x slower than target
- Data displayed incorrectly

**Medium (P2):**
- Visual issues
- Minor performance degradation
- Edge case not handled

**Low (P3):**
- Cosmetic issues
- Minor UX improvements

### Bug Log Template

```
Bug ID: BCA-BUG-001
Severity: [P0/P1/P2/P3]
Component: [Backend/API/Frontend/Integration]
Description: [Clear description of issue]
Steps to Reproduce:
1. [Step 1]
2. [Step 2]
Expected: [What should happen]
Actual: [What actually happens]
Status: [Open/In Progress/Fixed/Closed]
```

---

## Test Documentation

### Test Execution Report

```markdown
# Bar Chart Aggregation - Test Execution Report

**Date:** [Test Date]
**Tester:** [Name]
**Environment:** [Dev/Staging/Production]

## Summary
- Total Tests: [Number]
- Passed: [Number]
- Failed: [Number]
- Blocked: [Number]
- Not Run: [Number]

## Unit Tests
- Status: [✅ Passed / ❌ Failed]
- Coverage: [XX%]
- Failed Tests: [List if any]

## Integration Tests
- Status: [✅ Passed / ❌ Failed]
- Response Times: [All within targets / Issues noted]
- Failed Tests: [List if any]

## Manual Testing
- Scenarios Completed: [X of Y]
- Pass Rate: [XX%]
- Critical Issues: [Number]

## Performance Testing
- All benchmarks met: [Yes/No]
- Slowest operation: [Details]
- Memory usage: [Peak]

## Browser Compatibility
- Fully compatible: [List browsers]
- Minor issues: [List if any]
- Not compatible: [List if any]

## Accessibility
- WCAG 2.1 AA compliance: [Yes/No]
- Issues found: [List]

## Bugs Found
- Critical: [Number]
- High: [Number]
- Medium: [Number]
- Low: [Number]

## Recommendation
- [ ] Ready for production
- [ ] Needs fixes before production
- [ ] Blocked by [Issue]
```

---

## Definition of Done

- [ ] All unit tests pass (12/12)
- [ ] All integration tests pass (5/5)
- [ ] All manual test scenarios completed and documented
- [ ] Performance benchmarks met (<800ms for 1M rows)
- [ ] Browser compatibility verified (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility testing passed (WCAG 2.1 AA)
- [ ] Regression testing confirms no breaks
- [ ] Zero critical (P0) bugs
- [ ] Zero high (P1) bugs (or all fixed)
- [ ] Test execution report completed
- [ ] QA sign-off obtained

---

## Notes

- Automated tests should be run on every commit
- Manual testing required before each release
- Performance tests should use realistic datasets
- Browser testing on latest stable versions
- Accessibility testing required for WCAG compliance
