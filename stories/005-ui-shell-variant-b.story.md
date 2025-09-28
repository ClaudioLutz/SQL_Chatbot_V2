# Story 005: UI Shell Variant B

**Epic:** E4 - Visualize UI Epic  
**Priority:** P1  
**Labels:** `epic:E4`, `type:story`, `prio:P1`, `a11y`  
**Status:** Ready  

## API Integration Status
✅ **Ready for Development** - Backend APIs now available:
- `/api/generate` - LLM to SQL conversion endpoint (Story 003 complete)
- `/api/render` - Chart generation endpoint (Story 004 in Code Review)

WIP Limit: Respected - Story 005 can proceed with API integration testing

## Context

Build the main user interface shell with a three-tab layout (Chart | Details | Data) implementing WAI-ARIA manual-activation pattern for accessibility. Include a progress stepper showing the LLM→SQL→Execute→Render pipeline, download functionality for CSV/PNG, and integration points for backend APIs.

The UI must be fully accessible via keyboard and screen readers, with proper focus management and ARIA labeling. Initial implementation connects to mocked APIs to enable parallel development while backend components are completed.

## Story

**As a** user of the SQL Chatbot application  
**I want** an intuitive, accessible interface to input queries and view results in multiple formats  
**So that** I can effectively explore my data through charts, details, and raw data views

## Tasks

### Tab Interface with WAI-ARIA
- [ ] Implement three-tab layout: Chart | Details | Data
- [ ] Use WAI-ARIA manual-activation pattern (keyboard navigation without auto-activation)
- [ ] Proper tab list, tab, and tabpanel roles
- [ ] Keyboard navigation (arrow keys, Home, End, Tab, Space/Enter)
- [ ] Focus management and visual focus indicators
- [ ] Screen reader announcements for tab changes

### Progress Stepper Component
- [ ] Visual progress indicator: LLM → SQL → Execute → Render
- [ ] State management (pending, active, complete, error)
- [ ] Loading spinners and progress animations
- [ ] Error state visualization with retry options
- [ ] Accessible progress announcements for screen readers

### Chart Tab Implementation
- [ ] Image placeholder with loading states
- [ ] Chart display area with proper aspect ratio handling
- [ ] Chart caption display below image
- [ ] Error handling for failed chart generation
- [ ] Responsive design for various screen sizes

### Details Tab Implementation
- [ ] Collapsible sections for SQL query and Python visualization code
- [ ] Syntax highlighting for SQL and Python code
- [ ] Copy-to-clipboard functionality for code blocks
- [ ] Expandable/collapsible interface elements
- [ ] Proper heading structure for screen readers

### Data Tab Implementation
- [ ] Tabular data display with proper table markup
- [ ] Column sorting functionality (accessible)
- [ ] Pagination controls for large datasets
- [ ] Row/column count indicators
- [ ] Table caption and summary information

### Download Functionality
- [ ] CSV download button with progress indication
- [ ] PNG download button (when chart available)
- [ ] Download status feedback (success/error)
- [ ] File naming with timestamp/query info
- [ ] Keyboard accessible download triggers

### API Integration (Mocked)
- [ ] Query submission to LLM endpoint (mocked response)
- [ ] SQL execution endpoint integration (mocked data)
- [ ] Visualization generation endpoint (mocked chart)
- [ ] Error handling for all API interactions
- [ ] Loading states during API calls

## Acceptance Criteria

1. **Tab Navigation:** Manual-activation ARIA pattern works correctly with keyboard and screen reader
2. **Keyboard Accessibility:** All functionality accessible via keyboard navigation
3. **Screen Reader Support:** Proper announcements and labeling for all UI elements
4. **Progress Tracking:** Visual and accessible progress through the four-step pipeline
5. **Responsive Design:** Interface adapts to different screen sizes and devices
6. **Download Functionality:** CSV and PNG downloads work with proper user feedback
7. **Mocked Integration:** All API endpoints return realistic mocked data for development
8. **Error Handling:** Graceful error states with recovery options

## Definition of Done

- [ ] Tests green locally and in CI; minimal coverage on new code
- [ ] Accessibility: tab order, ARIA roles, color contrast checks where applicable
- [ ] Keyboard + screen-reader paths pass; placeholders render
- [ ] Config/docs updated (`.env.example`, `README_dev.md`)  
- [ ] Logs include correlation IDs; errors are user-safe (no secrets, no stack dumps)
- [ ] Performance: UI responds within 200ms for typical interactions
- [ ] Cross-browser compatibility verified (Chrome, Firefox, Safari, Edge)

## Dev Notes

### Technical Requirements
- HTML5 semantic markup with proper ARIA attributes
- CSS Grid/Flexbox for responsive layout
- Vanilla JavaScript or lightweight framework
- Progressive enhancement approach
- Modern browser support (ES6+)

### WAI-ARIA Manual-Activation Pattern
```html
<div class="tablist" role="tablist" aria-label="Query Results">
  <button role="tab" aria-selected="true" aria-controls="chart-panel" id="chart-tab">
    Chart
  </button>
  <button role="tab" aria-selected="false" aria-controls="details-panel" id="details-tab">
    Details
  </button>
  <button role="tab" aria-selected="false" aria-controls="data-panel" id="data-tab">
    Data
  </button>
</div>

<div role="tabpanel" id="chart-panel" aria-labelledby="chart-tab">
  <!-- Chart content -->
</div>
```

### Progress Stepper States
```javascript
const progressSteps = [
  { id: 'llm', label: 'Generating SQL', status: 'complete' },
  { id: 'sql', label: 'Validating Query', status: 'active' },
  { id: 'execute', label: 'Executing Query', status: 'pending' },
  { id: 'render', label: 'Creating Chart', status: 'pending' }
];
```

### Accessibility Requirements
- Color contrast ratio ≥ 4.5:1 for normal text
- Focus indicators visible and distinct
- Keyboard navigation follows logical tab order
- Screen reader announcements for state changes
- Alternative text for all images and icons
- Form labels properly associated

### Mocked API Responses
```javascript
// Mock LLM Response
{
  "sql": "SELECT TOP 10 ProductID, Name FROM dbo.Products ORDER BY ProductID",
  "explanation": "This query retrieves the first 10 products ordered by ProductID"
}

// Mock SQL Execution Response
{
  "data": [
    {"ProductID": 1, "Name": "Adjustable Race"},
    {"ProductID": 2, "Name": "Bearing Ball"}
  ],
  "rowCount": 2,
  "executionTime": "45ms"
}

// Mock Chart Response
{
  "imageData": "data:image/png;base64,iVBORw0KGgo...",
  "caption": "Bar chart showing product distribution",
  "chartType": "bar"
}
```

## Testing

### Unit Tests Required
- Tab navigation and ARIA implementation
- Progress stepper state management
- Download functionality triggers
- Keyboard event handling
- API integration with mocked responses
- Error state handling and recovery

### Accessibility Tests Required
- Automated accessibility scanning (axe or pa11y)
- Keyboard navigation testing
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Color contrast verification
- Focus management validation
- ARIA attribute correctness

### Integration Tests Required
- End-to-end user workflows with mocked APIs
- Cross-browser compatibility testing
- Responsive design validation
- Performance testing for UI interactions
- Error scenario testing

### Test Data
```javascript
// Test scenarios for mocked data
const testScenarios = [
  {
    query: "Show me top products",
    expectedSteps: ['llm', 'sql', 'execute', 'render'],
    mockData: { /* ... */ }
  },
  {
    query: "Invalid query",
    expectedError: "SQL validation failed",
    recoveryAction: "retry"
  }
];
```

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Tasks Completed
- [ ] Tab interface with WAI-ARIA implementation
- [ ] Progress stepper component
- [ ] Chart tab with placeholder rendering
- [ ] Details tab with code display
- [ ] Data tab with table display
- [ ] Download functionality (CSV/PNG)
- [ ] API integration with mocked responses
- [ ] Accessibility testing and validation
- [ ] Cross-browser compatibility testing

### Debug Log References
_To be filled by dev agent with links to specific debug sessions_

### Completion Notes
_To be filled by dev agent with implementation details and decisions_

### File List
_To be filled by dev agent with all new/modified/deleted files_

### Change Log
_To be filled by dev agent with detailed changes made_
