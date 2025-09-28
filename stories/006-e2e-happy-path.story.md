# Story 006: End-to-End Happy Path

**Epic:** E2+E3+E4 - Integration Story  
**Priority:** P1  
**Labels:** `epic:E2`, `epic:E3`, `epic:E4`, `type:story`, `prio:P1`  
**Status:** Ready  

## Context

Wire together the complete user journey from natural language query to visualized results, integrating the LLM-to-SQL wrapper (E2), visualization sandbox (E3), and UI shell (E4). This story demonstrates the full pipeline: prompt→SQL→execute→render, with proper error handling, progress tracking, and result display.

This integration story validates that all components work together seamlessly, providing users with a complete end-to-end experience including SQL/Python code visibility and CSV/PNG download functionality.

## Story

**As a** user of the SQL Chatbot application  
**I want** to input a natural language question and receive a complete response with chart, details, and data  
**So that** I can explore the AdventureWorks database through an intuitive conversational interface

## Tasks

### Pipeline Integration
- [ ] Wire LLM service to generate T-SQL from natural language input
- [ ] Connect SQL validator to ensure generated queries are safe
- [ ] Integrate SQL execution against AdventureWorks database
- [ ] Connect visualization service to generate charts from SQL results
- [ ] Ensure proper error propagation through the entire pipeline

### UI Integration & Flow
- [ ] Connect query input form to LLM endpoint
- [ ] Update progress stepper to reflect actual pipeline status
- [ ] Display generated SQL in Details tab with syntax highlighting
- [ ] Show visualization code (Python) in Details tab
- [ ] Render chart image in Chart tab with caption
- [ ] Display tabular data in Data tab with pagination

### Error Handling & Recovery
- [ ] Handle LLM API failures with user-friendly messages
- [ ] Process SQL validation errors with correction suggestions
- [ ] Manage database execution errors with repair attempts
- [ ] Handle visualization generation failures with fallbacks
- [ ] Provide retry mechanisms for transient failures

### Download & Export Features
- [ ] Generate CSV downloads from SQL execution results
- [ ] Provide PNG downloads of generated charts
- [ ] Include metadata in downloads (query, timestamp, parameters)
- [ ] Implement proper file naming and error handling
- [ ] Add download progress indicators and success feedback

### Demonstration Scenario
- [ ] Create a complete demo workflow using AdventureWorks data
- [ ] Test with realistic business questions (sales trends, product analysis)
- [ ] Validate the full pipeline with various query types
- [ ] Document the demo scenario for stakeholder presentations

## Acceptance Criteria

1. **Complete Pipeline:** User can input natural language and receive chart, SQL, and data
2. **Progress Tracking:** UI accurately reflects pipeline progress through all four stages
3. **SQL Visibility:** Generated and executed SQL visible in Details tab
4. **Chart Generation:** Visualization renders correctly with descriptive caption
5. **Data Display:** Tabular results display properly with sorting and pagination
6. **Downloads Work:** CSV and PNG downloads function with proper file naming
7. **Error Recovery:** Pipeline handles errors gracefully with user guidance
8. **Demo Scenario:** AdventureWorks demo scenario completes successfully end-to-end

## Definition of Done

- [ ] Tests green locally and in CI; minimal coverage on new code
- [ ] Demo scenario on AdventureWorks succeeds end-to-end
- [ ] Accessibility: tab order, ARIA roles, color contrast checks where applicable
- [ ] Config/docs updated (`.env.example`, `README_dev.md`)  
- [ ] Logs include correlation IDs; errors are user-safe (no secrets, no stack dumps)
- [ ] Performance: complete pipeline executes within 15 seconds for typical queries
- [ ] Documentation includes troubleshooting guide for common issues

## Dev Notes

### Technical Requirements
- Integration of all previous story components
- End-to-end error handling and logging
- Performance monitoring for the complete pipeline
- Demo data preparation and documentation

### Demo Scenario - AdventureWorks Product Analysis
```
User Input: "Show me the top 10 products by sales revenue"

Expected Pipeline:
1. LLM generates: SELECT TOP 10 p.Name, SUM(sod.LineTotal) as Revenue FROM dbo.Products p JOIN Sales.SalesOrderDetail sod ON p.ProductID = sod.ProductID GROUP BY p.Name ORDER BY Revenue DESC
2. Validator confirms query safety and deterministic ordering
3. Database executes query against AdventureWorks
4. Visualization generates bar chart of product revenue
5. UI displays chart, SQL code, Python code, and tabular data
6. Downloads available for CSV and PNG
```

### Integration Points Validation
```javascript
const integrationFlow = {
  input: "Natural language query",
  llm: "Generated T-SQL with schema context",
  validator: "Safety validation with error details",
  executor: "SQL execution with result data",
  visualizer: "Chart generation with PNG output",
  ui: "Complete result display with downloads"
};
```

### Error Scenarios to Test
- LLM API timeout or rate limiting
- SQL validation failures requiring repair
- Database connectivity issues
- Visualization rendering failures
- Large result sets requiring pagination
- Concurrent user requests

### Performance Targets
- LLM response: < 5 seconds
- SQL validation: < 100ms  
- Database execution: < 5 seconds
- Chart generation: < 3 seconds
- Total pipeline: < 15 seconds
- UI responsiveness: < 200ms

## Testing

### Integration Tests Required
- Complete end-to-end pipeline with real AdventureWorks data
- Error handling at each pipeline stage
- Progress tracking accuracy through all phases
- Download functionality with generated content
- Performance testing under realistic load
- Concurrent user scenario testing

### Demo Validation Tests
- Business intelligence scenarios (sales analysis, customer insights)
- Complex queries requiring joins and aggregations
- Edge cases (empty results, large datasets, malformed input)
- Error recovery and retry mechanisms
- User experience flow validation

### Performance Tests Required
- Pipeline execution time measurement
- Memory usage monitoring during visualization
- Database connection pooling efficiency
- LLM API response time tracking
- UI rendering performance with large datasets

### Test Data Scenarios
```sql
-- Demo queries for comprehensive testing
test_queries = [
  "What are our top selling products?",
  "Show sales trends by month for 2023", 
  "Which customers have the highest lifetime value?",
  "Compare bike sales across different categories",
  "What's the geographic distribution of our sales?"
]
```

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Tasks Completed
- [ ] Pipeline integration (LLM→SQL→Execute→Render)
- [ ] UI integration and flow management
- [ ] Error handling and recovery mechanisms
- [ ] Download and export features
- [ ] Demo scenario implementation
- [ ] End-to-end integration tests
- [ ] Performance optimization and testing
- [ ] Documentation and troubleshooting guides

### Debug Log References
_To be filled by dev agent with links to specific debug sessions_

### Completion Notes
_To be filled by dev agent with implementation details and decisions_

### File List
_To be filled by dev agent with all new/modified/deleted files_

### Change Log
_To be filled by dev agent with detailed changes made_
