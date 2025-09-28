# E4: Visualize UI (Variant B)

## Epic Goal

Transform the basic HTML interface into a comprehensive accessible "Visualize" window featuring Variant B tabs (Chart|Details|Data), progressive enhancement, WAI-ARIA compliance, and seamless integration with visualization and SQL safety layers.

## Epic Description

**Existing System Context:**

- Current functionality: Basic HTML form with text input, submit button, and simple table results display
- Technology stack: Static HTML/CSS/JS served from FastAPI, minimal JavaScript, no accessibility features
- Integration points: Form submission → FastAPI backend → JSON response → basic table rendering

**Enhancement Details:**

- What's being added/changed: Complete UI transformation with tabbed interface, progress stepper, ARIA live regions, keyboard navigation, CSV/PNG downloads, progressive enhancement
- How it integrates: Replaces existing static/index.html while maintaining FastAPI backend compatibility, adds client-side JavaScript for accessibility and tab management
- Success criteria: WCAG AA compliant interface, seamless keyboard navigation, graceful degradation without JavaScript, integrated visualization display

## Stories

1. **Story E4.1:** WAI-ARIA Tabbed Interface & Progress Stepper
   - Implement tabs following WAI-ARIA Authoring Practices with manual activation and roving tabindex
   - Create progressive stepper showing LLM→SQL→Execute→Render stages with ARIA live regions
   - Build keyboard navigation supporting Tab, Arrow keys, Enter/Space activation per accessibility standards

2. **Story E4.2:** Chart, Details & Data Tab Content
   - Design Chart tab with PNG visualization display, descriptive captions, and zoom/accessibility features
   - Create Details tab with collapsible SQL query and Python code sections (default collapsed)
   - Build enhanced Data tab with sortable table, pagination, and CSV download functionality

3. **Story E4.3:** Progressive Enhancement & Download Features
   - Implement graceful degradation ensuring basic functionality without JavaScript
   - Create CSV and PNG download system with proper file naming and accessibility labels
   - Build offline/timeout state handling with clear recovery options and user guidance

## Dependencies

**Requires:** E0 (Platform & DevEx), E1 (SQL Safety Layer), E2 (LLM→SQL Tooling), E3 (Visualization Sandbox)
**Blocks:** E5 (Observability & A11y QA) - UI must be complete before final accessibility validation

**Dependency Rationale:** UI requires all backend systems operational to display charts, execute safe queries, and provide comprehensive user experience.

## Compatibility Requirements

- [x] Maintain existing FastAPI backend API compatibility
- [x] Preserve current natural language input workflow and user expectations
- [x] Ensure static file serving continues to work for new assets (CSS, JS, PNG charts)
- [x] Keep existing error handling patterns while enhancing user experience

## Risk Mitigation

- **Primary Risk:** Complex JavaScript accessibility features conflict with progressive enhancement or break keyboard navigation
- **Mitigation:** Comprehensive accessibility testing, progressive enhancement validation, keyboard-only user testing throughout development
- **Rollback Plan:** Simplified tabbed interface fallback with basic ARIA support, maintaining core functionality

## Definition of Done

- [x] Tabbed interface follows WAI-ARIA Authoring Practices with proper keyboard navigation (Tab, Arrow, Enter/Space)
- [x] Progress stepper provides real-time updates via ARIA live regions (role="status" for updates, role="alert" for errors)
- [x] Chart tab displays PNG visualizations with descriptive captions and accessibility features
- [x] Details tab shows collapsible SQL query and Python code with syntax highlighting
- [x] Data tab provides sortable table, pagination, and CSV download functionality
- [x] Progressive enhancement ensures basic functionality without JavaScript
- [x] WCAG AA compliance verified: ≥4.5:1 contrast ratios, Target Size (Minimum), keyboard navigation
- [x] CSV and PNG downloads work with proper file naming and accessibility labels

## Integration Verification

- **IV-E4-01:** Existing natural language query workflow functions identically with enhanced UI
- **IV-E4-02:** Tabbed interface displays visualization pipeline results correctly (Chart, Details, Data)
- **IV-E4-03:** Keyboard-only navigation provides complete access to all functionality
- **IV-E4-04:** Progressive enhancement gracefully degrades to functional basic interface without JavaScript
- **IV-E4-05:** Download features provide properly formatted CSV data and PNG charts with appropriate file names

## Accessibility Acceptance Criteria

**AC-UI-A11Y-01:** Tab key navigation moves through tabs in logical order, arrow keys switch between tabs, Enter/Space activate tabs
**AC-UI-A11Y-02:** Progress stepper announces "Generating SQL query..." via aria-live="polite" during LLM processing
**AC-UI-A11Y-03:** Chart images include alt text with descriptive captions explaining data insights
**AC-UI-A11Y-04:** All interactive elements meet 44x44px minimum target size for touch accessibility
**AC-UI-A11Y-05:** Color contrast meets WCAG AA (≥4.5:1 for normal text, ≥3:1 for large text)

## User Experience Acceptance Criteria

**AC-UI-UX-01:** First-time users can successfully query "Top 10 products by sales" and view results in all three tabs without assistance
**AC-UI-UX-02:** JavaScript-disabled users can submit queries and view tabular results with basic styling
**AC-UI-UX-03:** CSV downloads include proper column headers and formatted data suitable for Excel/analysis tools
**AC-UI-UX-04:** PNG downloads provide publication-ready charts with appropriate resolution for presentations
**AC-UI-UX-05:** Error states provide clear recovery instructions and maintain user input during error resolution

## Performance Targets

- **Time-to-First-Visual:** ≤ 10 seconds from query submission to chart display
- **JavaScript Load Time:** ≤ 2 seconds for tab management and accessibility features
- **Responsive Design:** Functional on screen widths from 320px to 1920px
- **Keyboard Navigation:** Tab order completion ≤ 15 tab stops for complete interface traversal
- **Download Performance:** CSV/PNG generation ≤ 5 seconds for typical result sets

## Browser Compatibility

- **Modern Browsers:** Full functionality in Chrome 90+, Firefox 85+, Safari 14+, Edge 90+
- **Progressive Enhancement:** Basic functionality in browsers without modern JavaScript support
- **Screen Readers:** Tested compatibility with NVDA, JAWS, and VoiceOver
- **Mobile Accessibility:** Touch target compliance and responsive design for tablet/mobile usage
