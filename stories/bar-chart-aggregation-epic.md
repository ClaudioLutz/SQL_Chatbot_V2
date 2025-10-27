# Epic: Bar Chart Aggregation Feature

**Epic ID:** BCA-EPIC  
**Status:** Ready for Implementation  
**Priority:** High  
**Estimated Effort:** 5-6 hours  
**Target Release:** Q4 2025

---

## Epic Overview

**As a** data analyst working with large datasets (1M+ rows)  
**I want** bar charts to automatically aggregate duplicate categories  
**So that** I can visualize categorical distributions without manual data preparation

---

## Business Value

### Problem Statement

Current bar chart implementation blindly plots raw data without aggregation, causing:
- **Duplicate bars** for the same category (1M rows → 1M bars)
- **Browser crashes** with large datasets
- **Meaningless visualizations** - can't see distribution patterns
- **No frequency counting** - can't answer "how many of each?"

### Solution Benefits

- ✅ **Instant insights** - 1M rows → 8 bars in <1 second
- ✅ **Zero configuration** - auto-detects COUNT vs SUM aggregation
- ✅ **Performance** - backend aggregation handles any dataset size
- ✅ **Data transparency** - always shows what aggregation was performed

### Success Metrics

- 95% of 1M row aggregations complete in <500ms
- Bar chart usage increases by 30%
- Zero browser crashes on large datasets
- <1% error rate on aggregation requests

---

## Scope

### In Scope

**Core Aggregation:**
- Automatic backend aggregation for bar charts
- COUNT aggregation (frequency distribution)
- SUM aggregation (total values per category)
- AVG, MIN, MAX aggregation methods
- Top 50 category limiting (sorted by value)
- Auto-detection of aggregation method

**User Experience:**
- Transparent metadata display (rows aggregated, method used)
- Warning when categories limited
- Value formatting (K, M notation)
- Maintains existing visualization workflow

**Technical:**
- Backend implementation in `visualization_service.py`
- API integration in `main.py`
- Frontend enhancement in `app.js`
- Comprehensive testing

### Out of Scope (Future Enhancements)

- Manual aggregation method selector
- Configurable top N limit (fixed at 50)
- Horizontal bar orientation
- Color gradients by value
- Drill-down interactions
- Grouped/stacked bars
- Mobile optimization

---

## Architecture Overview

### Key Design Decisions

1. **Backend-Only Aggregation** - All aggregation on server using pandas
2. **Smart Auto-Detection** - No Y-axis = COUNT, With Y-axis = SUM
3. **Top 50 Limit** - Prevents chart clutter and performance issues
4. **Transparent Processing** - Users always know what happened

### Component Changes

```
app/
├── visualization_service.py  → Add prepare_bar_chart_data()
└── main.py                   → Update /api/visualize endpoint

static/
└── app.js                    → Update prepareChartDataClientSide()
```

### Data Flow

```
Query Results (1M rows)
    ↓
Backend Aggregation (pandas groupby)
    ↓
Top 50 Categories (sorted by value)
    ↓
API Response (~50 rows)
    ↓
Frontend Rendering (Plotly)
    ↓
Chart Display with Metadata
```

---

## User Stories

### Story BCA-001: Backend Aggregation Service
**Effort:** 2 hours  
**Priority:** Must Have  
**Dependencies:** None

Implement core aggregation logic in `visualization_service.py`
- `prepare_bar_chart_data()` function
- Support COUNT, SUM, AVG, MIN, MAX
- Auto-detection logic
- Top 50 limiting

### Story BCA-002: API Endpoint Integration
**Effort:** 1 hour  
**Priority:** Must Have  
**Dependencies:** BCA-001

Update `/api/visualize` endpoint to use aggregation for bar charts
- Conditional logic for bar chart type
- Request/response model updates
- Error handling
- Metadata return

### Story BCA-003: Frontend Chart Enhancement
**Effort:** 2 hours  
**Priority:** Must Have  
**Dependencies:** BCA-002

Update frontend to display aggregated data with metadata
- Enhanced `prepareChartDataClientSide()` for bar charts
- Metadata annotations
- Value formatting (K, M notation)
- Category limit warnings

### Story BCA-004: Testing & Quality Assurance
**Effort:** 1 hour  
**Priority:** Must Have  
**Dependencies:** BCA-001, BCA-002, BCA-003

Comprehensive testing across all layers
- Unit tests for aggregation logic
- Integration tests for API
- Manual testing with large datasets
- Edge case validation

---

## Technical Specifications

### Performance Requirements

| Metric | Target | Measurement |
|:-------|:-------|:------------|
| Aggregation (1M rows) | <500ms | Backend timing |
| Network Transfer | <100ms | 50 rows vs 1M rows |
| Chart Rendering | <200ms | Plotly render time |
| **Total End-to-End** | **<800ms** | User perception |

### Data Limits

- Maximum categories displayed: **50** (hard limit)
- Maximum dataset size: **No limit** (backend handles any size)
- Minimum rows for aggregation: **2** (validation)

### Aggregation Methods

| Method | Trigger | Use Case |
|:-------|:--------|:---------|
| COUNT | No Y-axis | Frequency distribution |
| SUM | Y-axis numeric, auto | Total per category |
| AVG | Y-axis numeric, manual | Average per category |
| MIN | Y-axis numeric, manual | Minimum per category |
| MAX | Y-axis numeric, manual | Maximum per category |

---

## Dependencies

### Technical Dependencies
- pandas 2.0.0+ (existing)
- FastAPI 0.103.1+ (existing)
- Plotly.js (via CDN, existing)
- Pydantic models (existing)

### Codebase Dependencies
- Existing sampling infrastructure
- Current visualization endpoint
- Tab-based UI system
- AG Grid results display

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|:-----|:------------|:-------|:-----------|
| Performance with 10M+ rows | Medium | High | Timeout at 5s, warning message |
| Memory issues | Low | Medium | Top 50 limit enforced |
| Breaking existing viz | Very Low | High | Isolated changes, comprehensive testing |
| User confusion | Low | Low | Clear metadata, auto-detection |

---

## Testing Strategy

### Test Scenarios

**Scenario 1: Frequency Count (No Y-axis)**
- Query: 1M rows, 8 unique statuses
- Expected: 8 bars showing count per status
- Verify: Title "Frequency Distribution", metadata accurate

**Scenario 2: Sum Aggregation (With Y-axis)**
- Query: 1M rows with Amount column
- Expected: Aggregated totals per category
- Verify: Title "Total Amount by Status", SUM method

**Scenario 3: Many Categories (150 unique)**
- Query: 500K rows, 150 products
- Expected: Top 50 products shown
- Verify: Warning "Showing top 50 of 150"

**Scenario 4: Edge Cases**
- All unique categories (no duplicates)
- NULL values in X-axis
- Single category only
- Zero values after aggregation
- Negative values

---

## Deployment Plan

### Implementation Phases

1. **Phase 1: Backend** (2 hours)
   - Implement `prepare_bar_chart_data()`
   - Add aggregation logic
   - Unit tests

2. **Phase 2: API** (1 hour)
   - Update `/api/visualize` endpoint
   - Request/response models
   - Error handling

3. **Phase 3: Frontend** (2 hours)
   - Update chart rendering
   - Metadata display
   - Value formatting

4. **Phase 4: Testing** (1 hour)
   - Integration tests
   - Performance benchmarks
   - Edge case validation

### Rollback Strategy

- All changes in isolated functions
- Easy to revert via git
- Feature flag pattern available if needed:
  ```python
  ENABLE_BAR_AGGREGATION = os.getenv("ENABLE_BAR_AGGREGATION", "true")
  ```

---

## Documentation

### User Documentation (Future)

**"Why are there only 50 categories shown?"**
> For readability, bar charts display the top 50 categories by default. This represents the highest values in your data.

**"What does 'aggregated' mean?"**
> When your data has duplicate categories, the system automatically combines them by counting or summing values.

### Technical Documentation

- Inline docstrings for all functions
- Architecture decision records
- Implementation guide (already created)
- API endpoint documentation

---

## Acceptance Criteria (Epic Level)

- [ ] All 4 user stories completed and accepted
- [ ] Performance targets met (<800ms end-to-end)
- [ ] All tests passing (unit + integration)
- [ ] Documentation complete
- [ ] Code reviewed and merged
- [ ] Deployed to production
- [ ] Success metrics tracked
- [ ] Zero critical bugs in first week

---

## Related Documents

- [Implementation Guide](../docs/bar-chart-aggregation-implementation.md)
- [Architecture Review](../docs/bar-chart-aggregation-architecture-review.md)
- [UX Specification](../docs/front-end-spec-bar-chart-aggregation.md)

---

**Epic Status:** Ready for Implementation  
**Created:** October 24, 2025  
**Owner:** Bob (Scrum Master)  
**Stakeholders:** PM, Architect, UX, Dev, QA
