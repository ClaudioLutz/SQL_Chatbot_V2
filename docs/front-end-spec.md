# Front-End Specification: Interactive Visualization Feature

**Version:** 2.0  
**Status:** Enhanced  
**Author:** Sally (UX Expert)  
**Last Updated:** January 10, 2025

## 1. Overview

This document provides the detailed front-end design, wireframes, and interaction specifications for the new Plotly-based visualization feature. It is based on the requirements from the brainstorming session and the architecture from the technical design document.

---

## 2. Component Breakdown and Wireframes

The visualization feature will be integrated into the existing tabbed interface.

### 2.1. Main Tab Interface (Unchanged)

The main tab structure remains the same. The "Visualizations" tab will be added.

```
+------------------------------------------------------------------+
| SQL Chatbot V2                                                   |
+------------------------------------------------------------------+
| [ Results ] [ Analysis ] [ Visualizations ]                      |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |         Content for the selected tab appears here            | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- The "Visualizations" tab will be disabled (`disabled` attribute and greyed out) if the query result is not suitable for visualization (e.g., fewer than 2 rows or no numeric columns). The backend should provide a flag for this.

---

### 2.2. Visualization Tab: Initial State

When the user clicks the "Visualizations" tab and a valid dataset is present, this is the initial view.

**Wireframe:**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Select a chart type to begin:                                   |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
|  | Scatter Plot|  |  Bar Chart  |  |  Line Chart |  | Histogram | |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |                                                              | |
| |          Select a chart type to configure your plot.         | |
| |                                                              | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- The chart type selectors are buttons. Clicking one will change the view to the "Configuration State".
- The main chart area displays a helpful prompt.

---

### 2.3. Visualization Tab: Configuration State (Bar Chart Example)

After the user selects a chart type, the UI updates to show relevant configuration options.

**Wireframe (Bar Chart Selected):**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Chart Type: [ Bar Chart v]                                      |
|                                                                  |
|  Categorical Axis (X): [ Select Column v]  Numeric Axis (Y): [ Select Column v] |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |                                                              | |
| |          Configure the axes to generate the chart.           | |
| |                                                              | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- The chart type selector is now a dropdown to allow for easy switching.
- The axis selectors ("Select Column") are dropdowns.
- **Crucially**, these dropdowns will only be populated with columns of the compatible type, as determined by the backend's column type detection.
    - **Bar Chart:** X-axis dropdown shows `categorical` columns; Y-axis dropdown shows `numeric` columns.
    - **Scatter Plot:** Both X and Y axis dropdowns show `numeric` columns.
    - **Line Chart:** X-axis dropdown shows `datetime` or `numeric` columns; Y-axis shows `numeric` columns.
    - **Histogram:** Only one dropdown appears for selecting a single `numeric` column.
- The chart area continues to show a prompt until both axes are selected.

---

### 2.4. Visualization Tab: Loading State

Once the required columns are selected, the chart begins to generate.

**Wireframe:**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Chart Type: [ Bar Chart v]                                      |
|                                                                  |
|  Categorical Axis (X): [ 'Product' v]  Numeric Axis (Y): [ 'Sales' v] |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |                  [ SKELETON LOADER ]                         | |
| |                  Generating chart...                         | |
| |                                                              | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- A skeleton loader (a simplified, greyed-out version of a chart) should be displayed to manage user expectation.
- A "Generating chart..." message provides context.
- All configuration controls should be disabled during loading to prevent changes.

---

### 2.5. Visualization Tab: Success State

The chart is successfully rendered.

**Wireframe:**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Chart Type: [ Bar Chart v]                                      |
|                                                                  |
|  Categorical Axis (X): [ 'Product' v]  Numeric Axis (Y): [ 'Sales' v] |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| | [        PLOTLY BAR CHART VISUALIZATION RENDERED         ]   | |
| |                                                              | |
| |                                                              | |
| |                                                              | |
| +--------------------------------------------------------------+ |
|  * Data sampled for performance. Displaying 10,000 of 50,000 rows. |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- The Plotly chart is interactive (zoom, pan, hover-over data points).
- If the data was sampled by the backend (for large datasets), a small notification must be displayed below the chart.

---

### 2.6. Visualization Tab: Error State

If chart generation fails for any reason.

**Wireframe:**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Chart Type: [ Bar Chart v]                                      |
|                                                                  |
|  Categorical Axis (X): [ 'Product' v]  Numeric Axis (Y): [ 'Sales' v] |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |          [!] Error generating chart.                         | |
| |          Incompatible data types for the selected axes.      | |
| |                                                              | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- A clear, user-friendly error message from the `appState.visualization.error` property should be displayed.
- The message should guide the user on how to fix the issue if possible (e.g., "Please select a numeric column for the Y-axis").

---

## 3. UI Mockups (ASCII Representation)

This section provides high-fidelity mockups represented as ASCII art, illustrating the look and feel of each state defined in the wireframes.

### 3.1. Initial State Mockup
*Clean, minimalist UI with clear action buttons.*
```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [_Visualizations_]                                         |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  Select a chart type to begin:                                                  |
|  +-----------------+  +-------------+  +--------------+  +-------------+        |
|  | 📊 Scatter Plot |  | 📶 Bar Chart |  | 📈 Line Chart |  | 📜 Histogram |        |
|  +-----------------+  +-------------+  +--------------+  +-------------+        |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| |                                                                             | |
| |                        Select a chart type to                               | |
| |                        configure your plot.                                 | |
| |                                                                             | |
| +-----------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------+
```

### 3.2. Configuration State Mockup
*Dropdowns appear for axis configuration, populated with compatible columns.*
```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [_Visualizations_]                                         |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  Chart Type: [ Bar Chart         ▼]                                             |
|                                                                                 |
|  Categorical Axis (X): [ Product Name      ▼]  Numeric Axis (Y): [ Sales   ▼]   |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| |                                                                             | |
| |                        Configure the axes to                                | |
| |                        generate the chart.                                  | |
| |                                                                             | |
| +-----------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------+
```

### 3.3. Loading State Mockup
*A skeleton loader provides visual feedback while the chart is generating.*
```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [_Visualizations_]                                         |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  Chart Type: [ Bar Chart         ▼] (disabled)                                  |
|                                                                                 |
|  Categorical Axis (X): [ Product Name      ▼] (disabled) Numeric Axis (Y): [ Sales   ▼] (disabled) |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| |    ██                                                                       | |
| |    ██ ██                                 Generating chart...                  | |
| | ██ ██ ██ ██                                                                 | |
| | ██ ██ ██ ██ ██                                                              | |
| +-----------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------+
```

### 3.4. Success State Mockup
*The Plotly chart is rendered, with a note about data sampling.*
```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [_Visualizations_]                                         |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  Chart Type: [ Bar Chart         ▼]                                             |
|                                                                                 |
|  Categorical Axis (X): [ Product Name      ▼]  Numeric Axis (Y): [ Sales   ▼]   |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| |    Sales by Product                                                         | |
| | 80 |    ██                                                                  | |
| | 60 | ██ ██ ██                                                              | |
| | 40 | ██ ██ ██ ██ ██                                                        | |
| | 20 +-----------------------------------------------------------------------| |
| |      Prod A  Prod B  Prod C  Prod D  Prod E                                 | |
| +-----------------------------------------------------------------------------+ |
|  * Data sampled for performance. Displaying 10,000 of 50,000 rows.              |
+---------------------------------------------------------------------------------+
```

### 3.5. Error State Mockup
*A clear, user-friendly error message is displayed.*
```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [_Visualizations_]                                         |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  Chart Type: [ Bar Chart         ▼]                                             |
|                                                                                 |
|  Categorical Axis (X): [ Product Name      ▼]  Numeric Axis (Y): [ Sales   ▼]   |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| |                                                                             | |
| |                        ⚠️ Error generating chart.                            | |
| |           Incompatible data types for the selected axes.                    | |
| |                                                                             | |
| +-----------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------+
```

---

## 4. Accessibility Specifications

**Compliance Target:** WCAG 2.1 Level AA

### 4.1. Keyboard Navigation

**Tab Sequence:**
1. Visualizations tab (when enabled)
2. Chart type selector buttons (in Initial State) / Chart type dropdown (in Configuration State)
3. X-axis column selector dropdown
4. Y-axis column selector dropdown (if applicable)
5. Chart interactive area (Plotly's built-in keyboard controls)

**Keyboard Interactions:**
- **Tab/Shift+Tab:** Navigate between controls
- **Enter/Space:** Activate buttons and open dropdowns
- **Arrow Keys:** Navigate dropdown options
- **Escape:** Close dropdowns or exit chart interaction mode
- **In Chart Area:** Plotly provides native keyboard zoom/pan controls

**Focus Management:**
- Visible focus indicator on all interactive elements (2px solid outline, color: `#0066CC`)
- Focus should not jump unexpectedly when chart renders
- When switching chart types, focus returns to chart type selector
- Skip link provided: "Skip to chart" for keyboard users when chart is rendered

### 4.2. Screen Reader Support

**ARIA Labels and Roles:**

```html
<!-- Tab button -->
<button role="tab" aria-controls="viz-panel" aria-selected="true">
  Visualizations
</button>

<!-- Chart type buttons (Initial State) -->
<button aria-label="Create scatter plot visualization">
  📊 Scatter Plot
</button>

<!-- Chart type dropdown (Configuration State) -->
<select aria-label="Select chart type">
  <option value="bar">Bar Chart</option>
  <!-- ... -->
</select>

<!-- Axis selectors -->
<select aria-label="Select column for X-axis (categorical data)">
  <option value="">Select Column</option>
  <!-- ... -->
</select>

<select aria-label="Select column for Y-axis (numeric data)">
  <option value="">Select Column</option>
  <!-- ... -->
</select>

<!-- Loading state -->
<div role="status" aria-live="polite" aria-atomic="true">
  Generating chart from Product Name and Sales columns...
</div>

<!-- Chart container -->
<div role="img" aria-label="Bar chart showing Sales by Product Name. X-axis: Product Name (5 categories). Y-axis: Sales ranging from 0 to 80.">
  <!-- Plotly chart renders here -->
</div>

<!-- Error state -->
<div role="alert" aria-live="assertive">
  Error generating chart. Incompatible data types for the selected axes. Please select a numeric column for the Y-axis.
</div>

<!-- Sampling notification -->
<div role="status" aria-live="polite">
  Data sampled for performance. Displaying 10,000 of 50,000 rows.
</div>
```

**Screen Reader Announcements:**
- Tab activation: "Visualizations tab selected"
- Chart type selection: "Bar chart selected. Configure axes to generate chart."
- Axis selection: "X-axis set to Product Name. Select Y-axis to generate chart."
- Chart generating: "Generating chart from Product Name and Sales columns..."
- Chart ready: "Chart generated successfully. Use arrow keys to explore chart data."
- Error: Immediate announcement of error message with guidance

### 4.3. Visual Design Requirements

**Color Contrast:**
- All text: Minimum 4.5:1 contrast ratio (WCAG AA)
- Large text (18pt+): Minimum 3:1 contrast ratio
- Interactive elements: Minimum 3:1 contrast against background
- Chart colors: Ensure data series have sufficient contrast (test with color blindness simulators)

**Focus Indicators:**
- Visible 2px outline on all focusable elements
- Color: `#0066CC` (sufficient contrast on light backgrounds)
- Never remove focus indicators with CSS

**Text Sizing:**
- Base font size: 16px minimum
- Allow browser text resizing up to 200% without loss of functionality
- Use relative units (rem, em) for all text sizing

**Touch Targets:**
- Minimum size: 44x44 pixels (WCAG AAA, recommended)
- Spacing: Minimum 8px between interactive elements

### 4.4. Content Accessibility

**Alternative Text:**
- Chart images have descriptive `aria-label` that summarizes the data
- Format: "{Chart Type} showing {Y-axis} by {X-axis}. {Key insights}."
- Example: "Bar chart showing Sales by Product Name. X-axis has 5 product categories. Y-axis shows sales values ranging from 20 to 80."

**Semantic HTML:**
- Use semantic HTML5 elements (`<button>`, `<select>`, not `<div>` with click handlers)
- Proper heading hierarchy (if adding section headers)
- Form elements properly associated with labels

**Error Handling:**
- Error messages have `role="alert"` for immediate announcement
- Errors are both color-coded AND have icons/text
- Never rely on color alone to convey information

### 4.5. Plotly Accessibility Configuration

**Enable Plotly's Accessibility Features:**
```javascript
const layout = {
  // ... other layout options
  
  // Accessibility
  'aria-label': generateChartAriaLabel(chartType, xColumn, yColumn, data),
  
  // Enable keyboard interactions
  dragmode: 'zoom', // Allows keyboard zoom
  
  // High contrast mode support
  paper_bgcolor: 'rgba(0,0,0,0)', // Transparent background
  plot_bgcolor: 'rgba(0,0,0,0)',
  
  // Font size for readability
  font: {
    size: 14,
    family: 'Arial, sans-serif'
  }
};

const config = {
  // Enable accessibility features
  displayModeBar: true,
  modeBarButtonsToAdd: ['hoverclosest', 'hovercompare'],
  
  // Keyboard shortcuts
  scrollZoom: true,
  
  // Screen reader support
  editable: false,
  staticPlot: false // Allows interactions
};
```

### 4.6. Testing Requirements

**Automated Testing:**
- axe-core or similar tool for WCAG compliance
- Lighthouse accessibility audit (target score: 90+)
- Color contrast analyzer

**Manual Testing:**
- Keyboard-only navigation testing
- Screen reader testing (NVDA on Windows, JAWS, VoiceOver on Mac)
- High contrast mode testing (Windows High Contrast)
- Browser zoom testing (up to 200%)
- Touch device testing

**User Testing:**
- Include users with disabilities in testing
- Test with assistive technologies
- Gather feedback on actual usage patterns

---

## 5. Responsive Design Strategy

### 5.1. Breakpoints

| Breakpoint | Min Width | Max Width | Target Devices | Layout Strategy |
|------------|-----------|-----------|----------------|-----------------|
| **Mobile** | 320px | 767px | Smartphones | Stacked vertical layout |
| **Tablet** | 768px | 1023px | Tablets, small laptops | Optimized horizontal layout |
| **Desktop** | 1024px | 1439px | Standard monitors | Full horizontal layout (current design) |
| **Wide** | 1440px | — | Large displays | Enhanced spacing, larger chart area |

### 5.2. Mobile Layout (< 768px)

**Configuration Area - Stacked Vertical:**
```
+----------------------------------+
| [Visualizations]                 |
|----------------------------------|
|                                  |
|  Chart Type:                     |
|  [ Bar Chart              ▼ ]    |
|                                  |
|  X-Axis (Categorical):           |
|  [ Product Name           ▼ ]    |
|                                  |
|  Y-Axis (Numeric):               |
|  [ Sales                  ▼ ]    |
|                                  |
| +------------------------------+ |
| |                              | |
| |    [    CHART AREA    ]      | |
| |                              | |
| +------------------------------+ |
+----------------------------------+
```

**Mobile Adaptations:**
- Chart type selector buttons become full-width stacked buttons (Initial State)
- All dropdowns expand to full width
- Touch targets: Minimum 44x44px
- Chart area: Minimum height 300px, expands to fill remaining viewport
- Plotly responsive mode enabled: `{responsive: true}`
- Hide Plotly mode bar by default on mobile (show on tap/long-press)
- Simplified tooltips (tap to show, tap outside to hide)

**Mobile-Specific Interactions:**
- Swipe between tabs (Results, Analysis, Visualizations)
- Pull-to-refresh on chart to regenerate
- Pinch-to-zoom on chart (Plotly native)
- Long-press on chart for context menu

### 5.3. Tablet Layout (768-1023px)

**Hybrid Horizontal/Vertical:**
```
+--------------------------------------------------------+
| [Results] [Analysis] [Visualizations]                  |
|--------------------------------------------------------|
|                                                        |
|  Chart Type: [ Bar Chart    ▼ ]                       |
|                                                        |
|  X-Axis: [ Product Name ▼ ]  Y-Axis: [ Sales  ▼ ]     |
|                                                        |
| +----------------------------------------------------+ |
| |                                                    | |
| |            [    CHART AREA    ]                    | |
| |                                                    | |
| +----------------------------------------------------+ |
+--------------------------------------------------------+
```

**Tablet Adaptations:**
- Horizontal layout for axis selectors (side-by-side)
- Larger touch targets (48x48px recommended)
- Plotly mode bar visible by default
- Chart area: Flexible height, minimum 400px
- Optimize for both portrait and landscape orientations

**Landscape Orientation:**
- Maximize chart area
- Configuration controls may collapse to top toolbar

**Portrait Orientation:**
- Similar to mobile but with more horizontal space
- Side-by-side axis selectors if screen width allows

### 5.4. Desktop & Wide Layouts (1024px+)

**Current design is optimized for desktop.**

**Wide Screen Enhancements (1440px+):**
- Increase maximum chart width to 1200px (centered)
- Add padding around chart area (24px vs 16px)
- Larger default font sizes (16px → 18px for labels)
- More generous spacing between controls (16px → 24px)

### 5.5. Responsive Chart Sizing

**Plotly Responsive Configuration:**
```javascript
const layout = {
  autosize: true,
  responsive: true,
  // Dynamic margins based on screen size
  margin: {
    l: window.innerWidth < 768 ? 40 : 60,
    r: window.innerWidth < 768 ? 20 : 40,
    t: window.innerWidth < 768 ? 40 : 60,
    b: window.innerWidth < 768 ? 60 : 80
  }
};

// Resize observer to handle window resizing
window.addEventListener('resize', () => {
  Plotly.Plots.resize('chart-container');
});
```

**Font Scaling:**
- Mobile: 12px base font for chart labels
- Tablet: 14px base font
- Desktop: 14px base font
- Wide: 16px base font

**Axis Label Rotation:**
- Mobile: Rotate X-axis labels 45° if more than 5 categories
- Desktop: Horizontal labels preferred, rotate if needed

### 5.6. Content Adaptation

**Priority-Based Display:**

**Mobile - Essential Only:**
- Chart type selector
- Required axis selectors
- Chart area
- Critical error messages
- Hide: Sampling notification (show as icon with tooltip)

**Tablet - Enhanced:**
- All configuration controls
- Chart area
- Sampling notification
- Help tooltips

**Desktop - Full Experience:**
- All controls
- Enhanced tooltips
- Additional chart options (if added in future)
- Export functionality (if added)

### 5.7. Progressive Enhancement

**Base Experience (All Devices):**
- Chart generation works
- Basic interactivity (zoom, pan via Plotly)
- Keyboard navigation
- Error handling

**Enhanced Experience (Tablet+):**
- Richer tooltips
- Mode bar controls visible
- Faster interactions
- Additional chart customization

**Optimal Experience (Desktop):**
- Full feature set
- Advanced interactions
- Multi-chart comparison (if added)
- Advanced export options

### 5.8. Testing Requirements

**Responsive Testing Checklist:**
- [ ] Test on physical devices: iPhone, Android, iPad, various desktop resolutions
- [ ] Test all breakpoints in browser dev tools
- [ ] Test portrait and landscape orientations
- [ ] Verify touch targets meet minimum size requirements
- [ ] Ensure charts render correctly at all sizes
- [ ] Test with browser zoom at 200%
- [ ] Verify no horizontal scrolling on mobile
- [ ] Test with real data of varying complexity

---

## 6. Interaction Specifications

### 6.1. Chart Type Switching Behavior

**Scenario: User switches from Bar Chart to Scatter Plot**

**Axis Retention Rules:**
1. **Compatible Axes:** Retain both if both are numeric
   - Bar Chart (X: categorical, Y: numeric) → Scatter Plot (X: numeric, Y: numeric)
   - **Result:** Clear X-axis (categorical not compatible), retain Y-axis
   
2. **Incompatible Axes:** Clear incompatible selections
   - Example: Line Chart (X: datetime, Y: numeric) → Histogram (single numeric column)
   - **Result:** Clear both axes, show single column selector

3. **Partially Compatible:** Retain compatible selections
   - Scatter Plot (X: numeric, Y: numeric) → Line Chart (X: datetime/numeric, Y: numeric)
   - **Result:** Retain Y-axis, clear X-axis (prompt user to select datetime or numeric)

**User Feedback:**
- When axes are cleared: Show subtle notification "Chart type changed. Please reconfigure axes."
- When axes retained: Show success notification "Axes compatible. Regenerating chart..."
- Auto-regenerate chart if all required axes are still valid

**Implementation:**
```javascript
function handleChartTypeChange(newChartType) {
  const currentX = appState.visualization.xColumn;
  const currentY = appState.visualization.yColumn;
  
  const compatibilityMatrix = {
    bar: { x: ['categorical'], y: ['numeric'] },
    scatter: { x: ['numeric'], y: ['numeric'] },
    line: { x: ['datetime', 'numeric'], y: ['numeric'] },
    histogram: { x: ['numeric'] }
  };
  
  const newRequirements = compatibilityMatrix[newChartType];
  
  // Check X-axis compatibility
  const xCompatible = currentX && newRequirements.x.includes(currentX.type);
  const yCompatible = currentY && newRequirements.y && newRequirements.y.includes(currentY.type);
  
  if (!xCompatible) appState.visualization.xColumn = null;
  if (!yCompatible) appState.visualization.yColumn = null;
  
  // Show appropriate message
  if (!xCompatible || !yCompatible) {
    showNotification('Chart type changed. Please reconfigure axes.', 'info');
  } else {
    showNotification('Axes compatible. Regenerating chart...', 'success');
    generateChart(); // Auto-regenerate if all axes valid
  }
}
```

### 6.2. Chart Update Strategy

**Real-time vs. Manual Update:**

**Chosen Strategy: Debounced Real-time Updates**

**Behavior:**
- When user selects X-axis: Wait 300ms, check if Y-axis also selected
- If both axes selected: Auto-generate chart
- If axis changed: Debounce 300ms, then regenerate
- No separate "Generate Chart" button needed

**Benefits:**
- Immediate feedback
- Fewer clicks
- Modern, responsive feel

**Debouncing Implementation:**
```javascript
let updateTimeout = null;

function handleAxisChange(axis, column) {
  clearTimeout(updateTimeout);
  
  appState.visualization[axis] = column;
  
  // Check if all required axes are selected
  const chartType = appState.visualization.chartType;
  const canGenerate = validateChartConfiguration(chartType, appState.visualization);
  
  if (canGenerate) {
    updateTimeout = setTimeout(() => {
      generateChart();
    }, 300); // 300ms debounce
  }
}
```

**Loading State Handling:**
- Disable all configuration controls during chart generation
- Show skeleton loader immediately
- If subsequent change made within 300ms, cancel previous request

**Alternative: Manual Update (Optional Toggle):**
- Advanced users may prefer manual control
- Add "Auto-update" checkbox in settings (if needed in future)

### 6.3. Multiple Visualizations

**Current Scope: Single Active Chart**

**Behavior:**
- Only one chart displayed at a time
- Switching configurations replaces current chart
- No chart history/comparison in v1

**Future Enhancement Path:**
- "Pin Chart" button to save configuration
- Side-by-side comparison mode
- Export multiple charts

### 6.4. Configuration Persistence

**Within Session:**
- Chart configuration persists when switching between Results/Analysis/Visualizations tabs
- Switching back to Visualizations tab shows last generated chart
- Configuration cleared when new query executed

**Implementation:**
```javascript
// On query execution
function handleNewQuery(results) {
  // Clear previous chart state
  appState.visualization = {
    chartType: null,
    xColumn: null,
    yColumn: null,
    chartData: null,
    isAvailable: checkVisualizationAvailable(results)
  };
  
  // Disable Visualizations tab if not available
  if (!appState.visualization.isAvailable) {
    document.querySelector('[data-tab="visualizations"]').disabled = true;
  }
}

// On tab switch
function handleTabChange(tabName) {
  if (tabName === 'visualizations') {
    // If chart was previously generated, re-render from saved state
    if (appState.visualization.chartData) {
      renderChart(appState.visualization.chartData);
    }
  }
}
```

**Across Sessions:**
- No persistence in v1 (cleared on page refresh)
- Future: Save configurations to localStorage or user preferences

### 6.5. Error Recovery

**Error Types and User Actions:**

**1. Incompatible Data Types**
- **Message:** "Incompatible data types for the selected axes. Please select a {required_type} column for the {axis}-axis."
- **User Action:** Change axis selection to compatible column
- **Recovery:** Auto-clear invalid selection, show compatible options only

**2. Backend Timeout**
- **Message:** "Chart generation timed out. This dataset may be too large. Try filtering your query results."
- **User Action:** Modify SQL query to reduce dataset size
- **Recovery:** Return to configuration state, allow retry

**3. Network Error**
- **Message:** "Unable to generate chart. Please check your connection and try again."
- **User Action:** Click "Retry" button
- **Recovery:** Attempt to regenerate with same configuration

**4. Empty Dataset**
- **Message:** "No data available for visualization. Please execute a query that returns results."
- **User Action:** Execute SQL query
- **Recovery:** Disable Visualizations tab until valid data available

**5. Single Row Dataset**
- **Message:** "At least 2 rows are required for visualization. Your query returned only 1 row."
- **User Action:** Modify query
- **Recovery:** Disable Visualizations tab

**Retry Mechanism:**
```javascript
function handleChartError(error) {
  appState.visualization.error = error.message;
  appState.visualization.isLoading = false;
  
  // Show error with retry button for transient errors
  if (error.type === 'network' || error.type === 'timeout') {
    showErrorWithRetry(error.message, () => {
      generateChart(); // Retry with same configuration
    });
  } else {
    showError(error.message); // Just show error, require user to fix
  }
}
```

### 6.6. Edge Case Handling

**1. Large Number of Columns (200+)**
- **Issue:** Dropdown becomes unwieldy
- **Solution:** 
  - Add search/filter functionality to dropdowns
  - Show most recently used columns at top
  - Implement virtual scrolling for performance

**Implementation:**
```javascript
function createColumnDropdown(columns, type) {
  const dropdown = document.createElement('select');
  
  // Add search functionality if > 20 columns
  if (columns.length > 20) {
    // Use Select2 or similar library for searchable dropdown
    $(dropdown).select2({
      placeholder: 'Search or select column...',
      width: '100%'
    });
  }
  
  return dropdown;
}
```

**2. Very Long Column Names (100+ characters)**
- **Issue:** Column names overflow UI
- **Solution:**
  - Truncate to 40 characters with ellipsis
  - Show full name in tooltip on hover
  - Full name visible in dropdown expanded state

**CSS:**
```css
.axis-selector option {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.axis-selector option:hover {
  /* Tooltip shows full text */
}
```

**3. Query Execution During Chart Generation**
- **Issue:** User executes new query while chart is generating
- **Solution:**
  - Cancel in-flight chart generation request
  - Show notification: "Previous chart cancelled. Execute new query first."
  - Clear visualization state
  - Disable Visualizations tab until new query completes

**Implementation:**
```javascript
let currentChartRequest = null;

async function generateChart() {
  // Cancel previous request if exists
  if (currentChartRequest) {
    currentChartRequest.cancel();
  }
  
  currentChartRequest = axios.CancelToken.source();
  
  try {
    const response = await axios.post('/api/visualize', data, {
      cancelToken: currentChartRequest.token
    });
    // ... handle response
  } catch (error) {
    if (axios.isCancel(error)) {
      console.log('Chart generation cancelled');
    }
  }
}
```

**4. Single Row Dataset**
- **Issue:** Cannot create meaningful visualization
- **Message:** "At least 2 rows are required for visualization. Your query returned only 1 row."
- **Solution:** Disable Visualizations tab, show helpful message

**5. All Text Columns (No Numeric Data)**
- **Issue:** No numeric data for Y-axis
- **Message:** "This dataset contains no numeric data. Visualizations require at least one numeric column. Try a query that returns numbers."
- **Solution:** Disable Visualizations tab with explanation

**6. Extremely Large Values (Scientific Notation)**
- **Issue:** Numbers like 1.23e+15 may not display well
- **Solution:**
  - Plotly handles scientific notation automatically
  - Ensure axis labels use appropriate formatting
  - Consider logarithmic scale for very large ranges

**7. Dataset with Nulls/Missing Values**
- **Issue:** Missing data points in visualization
- **Solution:**
  - Backend filters out null values before sending
  - Show notification: "X rows excluded due to missing values"
  - Document filtering behavior in API

**8. Unicode/Special Characters in Column Names**
- **Issue:** Column names with emojis or special characters
- **Solution:**
  - Sanitize for display but preserve original for backend
  - Ensure proper UTF-8 encoding throughout
  - Test with various character sets

**9. Backend Response Timeout (> 30 seconds)**
- **Issue:** Very large dataset takes too long
- **Message:** "Chart generation timed out (30s). This dataset may be too large. Try:\n- Reducing date range in query\n- Adding WHERE clause to filter data\n- Aggregating data with GROUP BY"
- **Solution:** Provide actionable guidance

**10. Browser Tab Switched During Generation**
- **Issue:** Chart generation in background tab
- **Solution:**
  - Continue generation in background
  - Show notification when complete: "Chart ready!"
  - Browser APIs handle this automatically

---

## 7. Component Library Integration

### 7.1. Existing Component Usage

**From Current App (static/app.js):**

**Tabs Component:**
- Use existing tab system for Results/Analysis/Visualizations
- Maintain consistent styling with current tabs
- Add Visualizations tab with same structure

**Button Styles:**
- Match existing query button styles for chart type selectors
- Use consistent hover/active states
- Maintain color scheme

**Dropdown Styles:**
- Use existing select element styling if present
- Ensure consistent appearance with other dropdowns in app
- Match font, size, spacing

### 7.2. New Components Required

**1. Chart Type Selector (Initial State)**
```css
.chart-type-selector {
  display: flex;
  gap: 12px;
  margin: 20px 0;
}

.chart-type-button {
  padding: 12px 20px;
  border: 2px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.chart-type-button:hover {
  border-color: #0066CC;
  background: #f0f7ff;
}

.chart-type-button:focus {
  outline: 2px solid #0066CC;
  outline-offset: 2px;
}

.chart-type-button .icon {
  font-size: 24px;
}
```

**2. Axis Configuration Controls**
```css
.axis-config {
  display: flex;
  gap: 16px;
  margin: 20px 0;
  align-items: end;
}

.axis-selector-wrapper {
  flex: 1;
}

.axis-selector-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.axis-selector {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.axis-selector:focus {
  outline: 2px solid #0066CC;
  border-color: #0066CC;
}

.axis-selector:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}
```

**3. Skeleton Loader**
```css
@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

.skeleton-chart {
  width: 100%;
  height: 400px;
  background: #f0f0f0;
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  padding: 20px;
  gap: 10px;
}

.skeleton-bar {
  flex: 1;
  background: #ddd;
  animation: pulse 1.5s ease-in-out infinite;
}

.skeleton-bar:nth-child(1) { height: 60%; }
.skeleton-bar:nth-child(2) { height: 80%; }
.skeleton-bar:nth-child(3) { height: 40%; }
.skeleton-bar:nth-child(4) { height: 90%; }
.skeleton-bar:nth-child(5) { height: 70%; }
```

**4. Notification Toast**
```css
.notification-toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  animation: slideIn 0.3s ease-out;
  z-index: 1000;
}

.notification-toast.info {
  background: #e3f2fd;
  border-left: 4px solid #2196F3;
  color: #0d47a1;
}

.notification-toast.success {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
  color: #1b5e20;
}

.notification-toast.error {
  background: #ffebee;
  border-left: 4px solid #f44336;
  color: #b71c1c;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

### 7.3. Design System Consistency

**Color Palette Alignment:**
- Primary: `#0066CC` (existing app primary)
- Success: `#4caf50`
- Error: `#f44336`
- Warning: `#ff9800`
- Neutral: `#757575`

**Typography:**
- Font Family: Inherit from existing app (likely system fonts)
- Base Size: 14px for controls, 16px for body text
- Headings: Follow existing hierarchy

**Spacing:**
- Unit: 8px base
- Gaps: 8px, 12px, 16px, 24px
- Margins: Match existing tab content spacing

**Elevation (Shadows):**
- Level 1: `0 2px 4px rgba(0,0,0,0.1)` (subtle)
- Level 2: `0 4px 12px rgba(0,0,0,0.15)` (notifications)
- Level 3: `0 8px 24px rgba(0,0,0,0.2)` (modals, if needed)

---

## 8. Performance Considerations

### 8.1. Chart Rendering Performance

**Optimization Strategies:**

**1. Data Sampling (Backend)**
- Automatically sample large datasets
- Threshold: 10,000 rows
- Sampling: Random or stratified (preserve distribution)
- Notify user of sampling

**2. Debouncing User Input**
- 300ms debounce on axis selection changes
- Prevents excessive API calls
- Better UX with immediate feedback

**3. Request Cancellation**
- Cancel in-flight requests when configuration changes
- Prevents rendering stale charts
- Axios CancelToken or AbortController

**4. Plotly Performance Configuration**
```javascript
const config = {
  // Disable animations for large datasets
  staticPlot: dataRows > 5000,
  
  // Reduce rendering complexity
  displayModeBar: true,
  displaylogo: false,
  
  // Optimize for performance
  responsive: true,
  useResizeHandler: true
};

// Simplify chart for large datasets
if (dataRows > 10000) {
  layout.hovermode = 'closest'; // Reduce hover calculations
  layout.dragmode = 'pan'; // Simpler than zoom
}
```

**5. Client-Side Caching**
- Cache generated chart configurations
- If user returns to same configuration, use cached data
- Clear cache on new query

```javascript
const chartCache = new Map();

function getCacheKey(chartType, xColumn, yColumn) {
  return `${chartType}-${xColumn}-${yColumn}`;
}

async function generateChart(config) {
  const key = getCacheKey(config.chartType, config.xColumn, config.yColumn);
  
  if (chartCache.has(key)) {
    renderChart(chartCache.get(key));
    return;
  }
  
  const chartData = await fetchChartData(config);
  chartCache.set(key, chartData);
  renderChart(chartData);
}
```

### 8.2. Memory Management

**Prevent Memory Leaks:**

```javascript
// Clean up Plotly instance when tab switches
function cleanupChart() {
  const chartContainer = document.getElementById('chart-container');
  if (chartContainer && Plotly.data) {
    Plotly.purge(chartContainer); // Clean up Plotly
  }
}

// Call when switching away from Visualizations tab
document.querySelectorAll('[data-tab]').forEach(tab => {
  tab.addEventListener('click', (e) => {
    if (e.target.dataset.tab !== 'visualizations') {
      cleanupChart();
    }
  });
});
```

### 8.3. Network Optimization

**1. Request Payload Optimization**
- Send only necessary columns (selected X, Y axes)
- Use backend filtering to reduce response size
- Compress large responses (gzip)

**2. Progressive Loading**
- For very large charts, consider streaming data
- Render initial view, then enhance with more data
- Show progress indicator

**3. Connection Resilience**
- Implement retry logic for failed requests (max 3 retries)
- Exponential backoff: 1s, 2s, 4s
- Clear error messages for network issues

### 8.4. Performance Targets

**Metrics:**

| Metric | Target | Maximum Acceptable |
|--------|--------|-------------------|
| Initial Tab Load | < 100ms | 200ms |
| Chart Type Selection | < 50ms | 100ms |
| Axis Selection (UI) | < 50ms | 100ms |
| Chart Generation (API) | < 2s | 5s |
| Chart Rendering (Client) | < 500ms | 1s |
| Total Time to Chart | < 3s | 6s |

**Monitoring:**
```javascript
// Performance tracking
function trackPerformance(action, startTime) {
  const duration = performance.now() - startTime;
  console.log(`[Perf] ${action}: ${duration.toFixed(2)}ms`);
  
  // Send to analytics if available
  if (window.analytics) {
    analytics.track('chart_performance', {
      action,
      duration,
      threshold_met: duration < getThreshold(action)
    });
  }
}
```

### 8.5. Browser Compatibility

**Target Browsers:**
- Chrome 90+ (primary)
- Firefox 88+
- Safari 14+
- Edge 90+

**Polyfills Required:**
- None for modern browsers
- Plotly handles cross-browser compatibility

**Feature Detection:**
```javascript
// Check for required features
const supportsVisualization = () => {
  return (
    'Promise' in window &&
    'fetch' in window &&
    'IntersectionObserver' in window
  );
};

if (!supportsVisualization()) {
  showError('Your browser does not support visualization features. Please upgrade to a modern browser.');
  disableVisualizationsTab();
}
```

---

## 9. Future Enhancements

### 9.1. Phase 2 Features

**1. Chart Customization Panel**
- Color scheme selection
- Title and axis label editing
- Legend position
- Grid line toggling

**2. Export Functionality**
- Export as PNG/SVG
- Export as CSV (underlying data)
- Copy chart to clipboard
- Share via URL

**3. Multiple Chart Comparison**
- Pin charts to workspace
- Side-by-side view (2-4 charts)
- Synchronized zoom/pan
- Comparison annotations

**4. Advanced Chart Types**
- Heatmap
- Box plot
- Pie/Donut chart
- Treemap
- Geographic maps (if location data)

**5. Chart Templates**
- Save chart configurations as templates
- Quick apply saved configurations
- Share templates with team
- Import/export templates

### 9.2. Phase 3 Features

**1. AI-Powered Insights**
- Auto-suggest optimal chart type based on data
- Highlight interesting patterns in data
- Natural language chart creation ("Show sales by region")

**2. Interactive Annotations**
- Add text annotations to charts
- Draw regions of interest
- Trend line overlays
- Reference lines

**3. Real-time Data Updates**
- Auto-refresh charts on data changes
- Live updating visualizations
- WebSocket support

**4. Collaborative Features**
- Share charts with specific users
- Comments on charts
- Version history
- Chart collections/dashboards

### 9.3. Technical Debt & Improvements

**Identified for Future Work:**

1. **Accessibility Audit** - Third-party audit by accessibility specialists
2. **Performance Profiling** - Detailed profiling with large datasets
3. **Mobile App** - Native mobile app with optimized visualizations
4. **Offline Support** - Service workers for offline chart viewing
5. **A/B Testing** - Test different UX patterns for optimal usability
6. **Internationalization** - Multi-language support for axis labels, messages

---

## 10. Developer Handoff Checklist

**Before Development Begins:**
- [ ] Review this specification with development team
- [ ] Clarify any ambiguous requirements
- [ ] Confirm technical feasibility of all features
- [ ] Align on coding standards and architecture patterns
- [ ] Set up development environment with necessary tools

**During Development:**
- [ ] Implement accessibility features from day one
- [ ] Test on multiple devices and browsers regularly
- [ ] Create unit tests for UI components
- [ ] Create integration tests for chart generation flow
- [ ] Document all deviations from spec with rationale

**Pre-Launch:**
- [ ] Complete accessibility audit (automated + manual)
- [ ] Perform cross-browser testing
- [ ] Conduct usability testing with real users
- [ ] Load test with large datasets
- [ ] Security review (if handling sensitive data)
- [ ] Update user documentation

**Post-Launch:**
- [ ] Monitor performance metrics
- [ ] Gather user feedback
- [ ] Track error rates and common issues
- [ ] Plan iteration based on learnings

---

## 11. Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| Jan 10, 2025 | 2.0 | Enhanced with accessibility, responsive design, interactions, component library, performance, and future enhancements | Sally (UX Expert) |
| Previous | 1.0 | Initial specification with wireframes and mockups | Sally (UX Expert) |

---

## 12. Appendix

### 12.1. Key Design Decisions

**Decision: Debounced Real-time Updates vs. Manual "Generate" Button**
- **Chosen:** Debounced real-time
- **Rationale:** Modern UX expectation, fewer clicks, immediate feedback
- **Trade-off:** Slightly more API calls, but acceptable with debouncing

**Decision: Single Chart vs. Multi-Chart View (v1)**
- **Chosen:** Single chart
- **Rationale:** Simpler implementation, most common use case
- **Future:** Multi-chart in Phase 2

**Decision: Client-side vs. Server-side Rendering**
- **Chosen:** Client-side with Plotly.js
- **Rationale:** Rich interactivity, lower server load, better performance
- **Trade-off:** Initial JavaScript payload size

**Decision: Tab Persistence**
- **Chosen:** Persist within session, clear on new query
- **Rationale:** Balances convenience with confusion prevention
- **Future:** Optional localStorage persistence

### 12.2. References

**Standards & Guidelines:**
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Plotly.js Documentation](https://plotly.com/javascript/)
- [MDN Web Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

**Inspiration:**
- Tableau visualization interface
- Google Data Studio chart builder
- Observable notebook visualizations

### 12.3. Contact

For questions or clarifications about this specification:
- **UX Lead:** Sally (UX Expert)
- **Review with:** Development Team, Product Owner

---

**End of Document**
