# Front-End Specification: Correlation Matrix Feature

**Version:** 1.0  
**Status:** Ready for Implementation  
**Author:** Sally (UX Expert)  
**Last Updated:** October 10, 2025

---

## 1. Overview

This document provides detailed front-end design, wireframes, and interaction specifications for the **Correlation Matrix visualization feature**. This feature extends the existing Visualizations tab with a new chart type that enables users to explore relationships between numeric variables through an interactive heatmap.

**Feature Summary:**
- **Integration Point:** New chart type in Visualizations tab
- **Primary Use Case:** Exploratory data analysis (EDA) to identify correlations
- **User Flow:** Chart type selection → Multi-select columns → Auto-generate heatmap
- **Key Innovation:** Smart defaults with pre-selected columns for instant insights

**Based on:**
- Architecture Document: `docs/correlation-matrix-feature-architecture.md`
- Existing Visualization Feature: `docs/visualisation-feature-architecture.md`

---

## 2. Component Breakdown and Wireframes

### 2.1. Correlation Matrix Chart Type Button

The correlation matrix is added as a new chart type alongside existing options.

**Wireframe: Chart Type Selector (Updated)**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Select a chart type to begin:                                   |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
|  | 📊 Scatter |  | 📶 Bar      |  | 📈 Line     |  | 📜 Histogram| |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
|  +------------------+                                            |
|  | 🔢 Correlation   |  [NEW]                                      |
|  |    Matrix        |                                            |
|  +------------------+                                            |
|                                                                  |
| +--------------------------------------------------------------+ |
| |          Select a chart type to configure your plot.         | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Visual Design:**
- Icon: 🔢 (representing matrix/numbers)
- Label: "Correlation Matrix"
- Same styling as existing chart type buttons
- Highlight on hover with border color change

---

### 2.2. Configuration State: Column Selector

After selecting "Correlation Matrix", the UI shows a multi-select column chooser.

**Wireframe: Configuration View**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Chart Type: [ Correlation Matrix ▼]                             |
|                                                                  |
|  Select Numeric Columns (2-10):                                  |
|  +------------------------------------------------------------+ |
|  | ☑ UnitPrice        ☑ Quantity        ☑ Discount           | |
|  | ☑ TotalSales       ☑ CustomerAge     ☐ OrderMonth        | |
|  | ☐ ProductID        ☐ ShipCost                            | |
|  +------------------------------------------------------------+ |
|  Select at least 2 columns. Maximum 10 recommended.              |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |          Select at least 2 columns to generate matrix.       | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- **Multi-select checkboxes** for intuitive column selection
- **Smart defaults:** First 5 numeric columns pre-selected
- **Only numeric columns shown** (filtered automatically)
- **Real-time validation:** Updates as user checks/unchecks
- **Auto-generation:** Chart appears 500ms after valid selection
- **Helper text:** Clear guidance on minimum/maximum columns

**Alternative for Many Columns (20+):**
```
+------------------------------------------------------------------+
|  Select Numeric Columns (2-10):                                  |
|  +------------------------------------------------------------+ |
|  | 🔍 Search columns...                                       | |
|  +------------------------------------------------------------+ |
|  | ☑ UnitPrice        ☑ Quantity        ☑ Discount           | |
|  | ☑ TotalSales       ☑ CustomerAge     ☐ OrderMonth        | |
|  | ☐ ProductID        ☐ ShipCost        ...                 | |
|  | [Show 8 more columns]                                     | |
|  +------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

---

### 2.3. Loading State

While the correlation matrix is being calculated.

**Wireframe: Loading State**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Chart Type: [ Correlation Matrix ▼] (disabled)                  |
|                                                                  |
|  Select Numeric Columns (2-10): (disabled)                       |
|  +------------------------------------------------------------+ |
|  | ☑ UnitPrice   ☑ Quantity   ☑ Discount   ☑ TotalSales     | |
|  | ☑ CustomerAge                                             | |
|  +------------------------------------------------------------+ |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |               [SKELETON LOADER - HEATMAP GRID]               | |
| |               Calculating correlations...                    | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Loading Indicators:**
- **Skeleton loader:** Simplified grid animation
- **Status text:** "Calculating correlations..." or "Generating matrix..."
- **Disabled controls:** All checkboxes disabled during generation
- **Progress indication:** For large datasets (>50K rows), show percentage
- **Cancellable:** Allow user to cancel if taking too long

---

### 2.4. Success State: Rendered Heatmap

The correlation matrix is successfully rendered as an interactive heatmap.

**Wireframe: Success State**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Chart Type: [ Correlation Matrix ▼]                             |
|                                                                  |
|  Select Numeric Columns (2-10):                                  |
|  ☑ UnitPrice  ☑ Quantity  ☑ Discount  ☑ TotalSales  ☑ CustomerAge|
|                                                                  |
| +--------------------------------------------------------------+ |
| |  Correlation Matrix                                          | |
| |                                                              | |
| |              Quantity  UnitPrice  Discount  TotalSales  Age  | |
| |  Quantity      1.00      0.12     -0.72      0.89      0.15 | |
| |  UnitPrice     0.12      1.00      0.03      0.45      0.08 | |
| |  Discount     -0.72      0.03      1.00     -0.34     -0.21 | |
| |  TotalSales    0.89      0.45     -0.34      1.00      0.22 | |
| |  CustomerAge   0.15      0.08     -0.21      0.22      1.00 | |
| |                                                              | |
| |  [Colors: Red (negative) ← White (0) → Blue (positive)]     | |
| +--------------------------------------------------------------+ |
|  ℹ Data sampled for performance. Displaying 10,000 of 50,000 rows.|
+------------------------------------------------------------------+
```

**Visual Elements:**
- **Heatmap cells:** Colored by correlation strength (RdBu colorscale)
- **Annotations:** Correlation values displayed on each cell (2 decimals)
- **Color legend:** Vertical bar showing -1.0 to +1.0 scale
- **Hover tooltips:** Detailed information on hover
- **Diagonal highlighting:** Self-correlations (1.0) in distinct shade
- **Interactive:** Zoom, pan, hover via Plotly controls

**Sampling Notice:**
- Shown only when data is sampled (>10K rows)
- Subtle, non-intrusive placement below chart
- Information icon (ℹ) for consistency

---

### 2.5. Error State

If correlation matrix generation fails.

**Wireframe: Error State**
```
+------------------------------------------------------------------+
| [ Visualizations ]                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Chart Type: [ Correlation Matrix ▼]                             |
|                                                                  |
|  Select Numeric Columns (2-10):                                  |
|  ☑ UnitPrice  ☑ Quantity  ☑ Discount  ☑ TotalSales             |
|                                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |          ⚠️ Error generating correlation matrix.              | |
| |                                                              | |
| |          Insufficient data after removing missing values.    | |
| |          At least 2 complete rows required.                  | |
| |                                                              | |
| |          [Try Different Columns]                             | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Error Types & Messages:**

**1. Insufficient Columns Selected**
```
❌ Please select at least 2 columns for correlation analysis.
```

**2. Too Many Columns**
```
⚠️ Maximum 10 columns recommended for readability.
   (Hard limit: 15 columns)
```

**3. Non-Numeric Columns** (shouldn't happen due to filtering)
```
❌ All selected columns must be numeric.
   Please select numeric columns only.
```

**4. Insufficient Data**
```
⚠️ Insufficient data after removing missing values.
   At least 2 complete rows required for correlation calculation.
```

**5. Backend Timeout**
```
⏱️ Correlation calculation timed out (30s).
   This dataset may be too large.
   
   Try:
   • Reducing the number of columns
   • Filtering your query to reduce row count
   • Selecting a smaller date range
```

**6. Network Error**
```
🌐 Unable to generate correlation matrix.
   Please check your connection and try again.
   
   [Retry]
```

---

## 3. High-Fidelity Mockups

### 3.1. Initial State - Chart Type Selection

*Clean interface with clear call-to-action*

```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [★ Visualizations]                                        |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  Select a chart type to begin:                                                  |
|                                                                                 |
|  +-----------------+  +---------------+  +-----------------+  +---------------+ |
|  | 📊             |  | 📶            |  | 📈              |  | 📜            | |
|  | Scatter Plot   |  | Bar Chart     |  | Line Chart      |  | Histogram     | |
|  +-----------------+  +---------------+  +-----------------+  +---------------+ |
|                                                                                 |
|  +------------------------+                                                     |
|  | 🔢                    |  ← NEW                                              |
|  | Correlation Matrix    |                                                     |
|  +------------------------+                                                     |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| |                                                                             | |
| |                   Select a chart type to configure your plot.               | |
| |                                                                             | |
| |                   💡 Tip: Use Correlation Matrix to discover                | |
| |                   relationships between numeric variables.                  | |
| |                                                                             | |
| +-----------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------+
```

**Design Specifications:**
- **Button size:** 180px × 100px
- **Icon size:** 32px
- **Font:** 14px, medium weight
- **Spacing:** 12px gap between buttons
- **Hover effect:** Border color changes to primary blue (#0066CC)
- **Focus indicator:** 2px solid outline

---

### 3.2. Configuration State with Smart Defaults

*First 5 numeric columns pre-selected for instant insights*

```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [★ Visualizations]                                        |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  Chart Type: [ Correlation Matrix                                          ▼ ] |
|                                                                                 |
|  Select Numeric Columns (2-10):                                                 |
|  ┌───────────────────────────────────────────────────────────────────────────┐ |
|  │ ✓ UnitPrice           ✓ Quantity           ✓ Discount                    │ |
|  │                                                                           │ |
|  │ ✓ TotalSales          ✓ CustomerAge        ☐ OrderMonth                 │ |
|  │                                                                           │ |
|  │ ☐ ProductID           ☐ ShipCost           ☐ Tax                         │ |
|  └───────────────────────────────────────────────────────────────────────────┘ |
|  ℹ Select at least 2 columns. Maximum 10 recommended for readability.           |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| |                                                                             | |
| |                    [⚙️ Generating matrix...]                                 | |
| |                                                                             | |
| +-----------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------+
```

**Smart Defaults Behavior:**
- **Automatic pre-selection:** First 5 numeric columns checked on load
- **Immediate generation:** Matrix starts generating automatically
- **Clear feedback:** Loading indicator appears immediately
- **User control:** Can modify selection while loading (cancels previous)

---

### 3.3. Success State - Rendered Heatmap

*Interactive correlation matrix with color-coded cells*

```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [★ Visualizations]                                        |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  Chart Type: [ Correlation Matrix                                          ▼ ] |
|                                                                                 |
|  ☑ UnitPrice  ☑ Quantity  ☑ Discount  ☑ TotalSales  ☑ CustomerAge              |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| |  Correlation Matrix                                                         | |
| |                                                                             | |
| |              Quantity  UnitPrice  Discount  TotalSales  CustomerAge         | |
| |                                                                             | |
| |  Quantity     [1.00]    [0.12]    [-0.72]   [0.89]     [0.15]              | |
| |  UnitPrice    [0.12]    [1.00]    [0.03]    [0.45]     [0.08]              | |
| |  Discount     [-0.72]   [0.03]    [1.00]    [-0.34]    [-0.21]             | |
| |  TotalSales   [0.89]    [0.45]    [-0.34]   [1.00]     [0.22]              | |
| |  CustomerAge  [0.15]    [0.08]    [-0.21]   [0.22]     [1.00]              | |
| |                                                                             | |
| |  Legend: -1.0 [████ Red] 0.0 [░░░░ White] +1.0 [████ Blue]                 | |
| |                                                                             | |
| |  🔍 Hover over cells for details | 🖱️ Click and drag to zoom                | |
| +-----------------------------------------------------------------------------+ |
|  ℹ Data sampled for performance. Displaying 10,000 of 50,000 rows.              |
+---------------------------------------------------------------------------------+
```

**Color Coding:**
- **Strong negative (-1.0 to -0.5):** Dark red (#d32f2f)
- **Weak negative (-0.5 to -0.2):** Light red (#ef5350)
- **No correlation (-0.2 to +0.2):** White/light gray (#f5f5f5)
- **Weak positive (+0.2 to +0.5):** Light blue (#42a5f5)
- **Strong positive (+0.5 to +1.0):** Dark blue (#1976d2)
- **Diagonal (self-correlation):** Distinct purple (#9c27b0) or keep as dark blue

**Text Annotations:**
- **Font size:** 12px
- **Color:** White text on dark cells (|r| > 0.5), black on light cells
- **Format:** Always 2 decimal places (e.g., "0.89", "-0.72")

---

### 3.4. Hover Tooltip

*Detailed information on mouse hover*

```
+---------------------------------------------------------------------------------+
|                                                                                 |
|              Quantity  UnitPrice  Discount  TotalSales  CustomerAge             |
|                                                                                 |
|  Quantity     [1.00]    [0.12]    [-0.72] ← ┌──────────────────────┐          |
|  UnitPrice    [0.12]    [1.00]    [0.03]    │ Quantity vs Discount │          |
|  Discount     [-0.72]   [0.03]    [1.00]    │                      │          |
|  TotalSales   [0.89]    [0.45]    [-0.34]   │ Correlation: -0.722  │          |
|  CustomerAge  [0.15]    [0.08]    [-0.21]   │                      │          |
|                                              │ Strong negative      │          |
|                                              │ relationship         │          |
|                                              └──────────────────────┘          |
+---------------------------------------------------------------------------------+
```

**Tooltip Content:**
- **Variable names:** "{Variable 1} vs {Variable 2}"
- **Correlation value:** 3 decimal places for precision
- **Interpretation:** 
  - Strong positive (r > 0.7)
  - Moderate positive (0.3 < r ≤ 0.7)
  - Weak positive (0.1 < r ≤ 0.3)
  - No correlation (-0.1 ≤ r ≤ 0.1)
  - Weak negative (-0.3 ≤ r < -0.1)
  - Moderate negative (-0.7 ≤ r < -0.3)
  - Strong negative (r < -0.7)

**Plotly Hover Configuration:**
```javascript
hovertemplate: 
  '<b>%{y}</b> vs <b>%{x}</b><br>' +
  'Correlation: %{z:.3f}<br>' +
  '<extra></extra>'
```

---

### 3.5. Advanced Configuration (Collapsed by Default)

*Optional sampling configuration for power users*

```
+---------------------------------------------------------------------------------+
|  ☑ UnitPrice  ☑ Quantity  ☑ Discount  ☑ TotalSales  ☑ CustomerAge              |
|                                                                                 |
|  ▸ Advanced: Sampling Configuration                                            |
|                                                                                 |
| [When expanded:]                                                                |
|  ▾ Advanced: Sampling Configuration                                            |
|  ┌───────────────────────────────────────────────────────────────────────────┐ |
|  │ Max Rows: [10000        ]  (0 = no limit)                                │ |
|  │                                                                           │ |
|  │ ℹ Default: 10,000 rows (recommended for datasets >1M rows).               │ |
|  │   Set to 0 to process full dataset (slower for large data).              │ |
|  └───────────────────────────────────────────────────────────────────────────┘ |
+---------------------------------------------------------------------------------+
```

**Configuration Options:**
- **Max Rows:** Number input, default 10000
- **Help text:** Explains impact of changing value
- **Collapsed by default:** Reduces visual clutter for most users
- **Saves to session:** Remembers user preference during session

---

## 4. Accessibility Specifications

### 4.1. Keyboard Navigation

**Tab Sequence:**
1. Visualizations tab
2. Chart type dropdown
3. Column checkboxes (in order)
4. Advanced configuration toggle (if visible)
5. Chart interactive area

**Keyboard Shortcuts:**
- **Tab/Shift+Tab:** Navigate between controls
- **Space:** Toggle checkbox or open dropdown
- **Enter:** Activate button or confirm selection
- **Arrow keys:** Navigate dropdown options
- **Escape:** Close dropdown or exit chart interaction
- **Ctrl+A:** Select all columns (in checkbox list)
- **Ctrl+D:** Deselect all columns

**Focus Management:**
```javascript
// Ensure focus doesn't jump when chart renders
function renderCorrelationMatrix(data) {
  const activeElement = document.activeElement;
  
  // Render chart
  Plotly.newPlot('chart-container', data, layout, config);
  
  // Restore focus if it was in the configuration area
  if (activeElement && activeElement.closest('.correlation-config')) {
    activeElement.focus();
  }
}
```

### 4.2. Screen Reader Support

**ARIA Labels:**

```html
<!-- Chart type dropdown -->
<select 
  aria-label="Select chart type"
  aria-describedby="chart-type-hint">
  <option value="correlation">Correlation Matrix</option>
</select>
<span id="chart-type-hint" class="sr-only">
  Choose a visualization type. Correlation Matrix shows relationships between numeric variables.
</span>

<!-- Column checkbox list -->
<fieldset aria-labelledby="column-selector-label">
  <legend id="column-selector-label">
    Select Numeric Columns (2-10)
  </legend>
  
  <label class="column-checkbox">
    <input 
      type="checkbox" 
      value="UnitPrice" 
      checked
      aria-describedby="col-unitprice-hint">
    <span>UnitPrice</span>
  </label>
  <span id="col-unitprice-hint" class="sr-only">
    Numeric column. Currently selected.
  </span>
  
  <!-- Repeat for other columns -->
</fieldset>

<!-- Helper text -->
<div role="status" aria-live="polite" id="column-selection-status">
  5 columns selected. Valid selection. Matrix will generate automatically.
</div>

<!-- Loading state -->
<div role="status" aria-live="polite" aria-busy="true">
  <span class="sr-only">Calculating correlation matrix for 5 columns...</span>
  <div class="skeleton-loader" aria-hidden="true"></div>
</div>

<!-- Chart container -->
<div 
  id="chart-container"
  role="img"
  aria-label="Correlation matrix heatmap showing relationships between 5 variables: UnitPrice, Quantity, Discount, TotalSales, and CustomerAge. Strongest positive correlation: TotalSales and Quantity (0.89). Strongest negative correlation: Discount and Quantity (-0.72)."
  tabindex="0">
  <!-- Plotly chart -->
</div>

<!-- Sampling notice -->
<div role="status" aria-live="polite">
  <span class="sr-only">Note: </span>
  Data sampled for performance. Displaying 10,000 of 50,000 rows.
</div>

<!-- Error state -->
<div role="alert" aria-live="assertive">
  <span class="sr-only">Error: </span>
  Insufficient data after removing missing values. At least 2 complete rows required for correlation calculation.
</div>
```

**Screen Reader Announcements:**

| Event | Announcement |
|-------|-------------|
| Correlation Matrix selected | "Correlation Matrix selected. Multi-select checkboxes for numeric columns now available." |
| Column checked | "UnitPrice selected. 5 columns selected. Matrix will generate." |
| Column unchecked | "Quantity deselected. 4 columns selected. Matrix will generate." |
| Below minimum (1 column) | "Only 1 column selected. Select at least 2 columns for correlation analysis." |
| Generating | "Calculating correlation matrix for 5 columns: UnitPrice, Quantity, Discount, TotalSales, CustomerAge." |
| Generated successfully | "Correlation matrix generated successfully. Interactive heatmap now displayed. Use arrow keys to explore correlations." |
| Error | "Error generating correlation matrix. {specific error message}" |

### 4.3. Color Accessibility

**Color Contrast:**
- All text meets WCAG AA: 4.5:1 minimum contrast ratio
- Correlation values: White on dark cells, black on light cells
- Helper text: #757575 on white background (4.6:1 ratio)
- Error messages: #d32f2f on white background (4.9:1 ratio)

**Color Independence:**
- Never rely on color alone to convey information
- Correlation values always shown as text annotations
- Tooltips provide textual interpretation
- Color legend includes numeric scale

**Color Blindness Considerations:**
- **RdBu colorscale** chosen for red-green color blindness compatibility
- Alternative: Offer "viridis" or "plasma" colorscales (future enhancement)
- Test with simulators: Deuteranopia, Protanopia, Tritanopia

**High Contrast Mode:**
```css
@media (prefers-contrast: high) {
  .column-checkbox input[type="checkbox"] {
    border: 2px solid #000;
  }
  
  .chart-container {
    border: 2px solid #000;
  }
  
  /* Ensure Plotly respects high contrast */
  .plotly .heatmap {
    outline: 1px solid #000;
  }
}
```

### 4.4. Alternative Text Generation

**Dynamic Chart Description:**
```javascript
function generateChartAriaLabel(correlationMatrix, columns) {
  // Find strongest correlations
  let strongestPositive = { value: -1, pair: [] };
  let strongestNegative = { value: 1, pair: [] };
  
  columns.forEach((col1, i) => {
    columns.forEach((col2, j) => {
      if (i < j) { // Avoid duplicates and diagonal
        const corr = correlationMatrix[col1][col2];
        if (corr > strongestPositive.value) {
          strongestPositive = { value: corr, pair: [col1, col2] };
        }
        if (corr < strongestNegative.value) {
          strongestNegative = { value: corr, pair: [col1, col2] };
        }
      }
    });
  });
  
  const description = 
    `Correlation matrix heatmap showing relationships between ${columns.length} variables: ${columns.join(', ')}. ` +
    `Strongest positive correlation: ${strongestPositive.pair[0]} and ${strongestPositive.pair[1]} (${strongestPositive.value.toFixed(2)}). ` +
    `Strongest negative correlation: ${strongestNegative.pair[0]} and ${strongestNegative.pair[1]} (${strongestNegative.value.toFixed(2)}).`;
  
  return description;
}
```

### 4.5. Touch and Mobile Accessibility

**Touch Target Sizes:**
- Minimum: 44×44 pixels (WCAG AAA)
- Checkboxes: 48×48px touch area (larger than visual)
- Buttons: 48×48px minimum

**Touch Interactions:**
- **Tap:** Select checkbox
- **Long press:** Show tooltip/help
- **Pinch:** Zoom chart
- **Swipe:** Pan chart (if zoomed)

**Implementation:**
```css
.column-checkbox {
  min-width: 44px;
  min-height: 44px;
  padding: 12px; /* Increases touch area beyond visual */
  display: inline-flex;
  align-items: center;
}

.column-checkbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin-right: 8px;
}
```

---

## 5. Responsive Design

### 5.1. Breakpoints

| Breakpoint | Min Width | Layout Strategy |
|------------|-----------|-----------------|
| Mobile | 320-767px | Stacked vertical, full-width controls |
| Tablet | 768-1023px | Hybrid layout, 2-column checkboxes |
| Desktop | 1024-1439px | Current design (optimal) |
| Wide | 1440px+ | Enhanced spacing, larger chart |

### 5.2. Mobile Layout (< 768px)

**Stacked Configuration:**
```
+----------------------------------+
| [Visualizations]                 |
|----------------------------------|
|                                  |
| Chart Type:                      |
| [ Correlation Matrix        ▼ ]  |
|                                  |
| Select Columns (2-10):           |
| ┌──────────────────────────────┐ |
| │ ✓ UnitPrice                  │ |
| │ ✓ Quantity                   │ |
| │ ✓ Discount                   │ |
| │ ✓ TotalSales                 │ |
| │ ✓ CustomerAge                │ |
| │ ☐ OrderMonth                 │ |
| │ [2 more...]                  │ |
| └──────────────────────────────┘ |
|                                  |
| +------------------------------+ |
| |     [CHART AREA]             | |
| |     (400px min height)       | |
| +------------------------------+ |
+----------------------------------+
```

**Mobile Adaptations:**
- Full-width dropdowns and checkbox areas
- Vertical scrolling for many columns
- Minimum 44×44px touch targets
- Chart: 100% width, 400px minimum height
- Simplified Plotly mode bar (hide by default, show on tap)
- Larger font sizes (16px base)

### 5.3. Tablet Layout (768-1023px)

**Two-Column Checkboxes:**
```
+--------------------------------------------------------+
| [Visualizations]                                       |
|--------------------------------------------------------|
|                                                        |
| Chart Type: [ Correlation Matrix              ▼ ]     |
|                                                        |
| Select Columns (2-10):                                 |
| ┌────────────────────────────────────────────────────┐|
| │ ✓ UnitPrice        ✓ Quantity                      │|
| │ ✓ Discount         ✓ TotalSales                    │|
| │ ✓ CustomerAge      ☐ OrderMonth                    │|
| └────────────────────────────────────────────────────┘|
|                                                        |
| +----------------------------------------------------+ |
| |          [CHART AREA - 600px height]               | |
| +----------------------------------------------------+ |
+--------------------------------------------------------+
```

**Tablet Optimizations:**
- 2-column checkbox grid for better space usage
- Chart expands to utilize screen width
- Mode bar visible by default
- Larger touch targets (48×48px)
- Chart height: 600px (more vertical space)

### 5.4. Desktop & Wide Layouts

**Desktop (1024-1439px):** Current design optimized

**Wide Screen (1440px+):**
- Maximum chart width: 1200px (centered)
- Enhanced padding: 24px vs 16px
- Larger default font sizes
- More generous spacing between controls

### 5.5. Responsive Chart Configuration

```javascript
function getChartDimensions() {
  const width = window.innerWidth;
  
  if (width < 768) {
    // Mobile
    return {
      width: '100%',
      height: 400,
      margin: { l: 40, r: 20, t: 40, b: 60 },
      fontSize: 12
    };
  } else if (width < 1024) {
    // Tablet
    return {
      width: '100%',
      height: 600,
      margin: { l: 60, r: 40, t: 60, b: 80 },
      fontSize: 14
    };
  } else {
    // Desktop
    return {
      width: 700,
      height: 700,
      margin: { l: 100, r: 100, t: 100, b: 100 },
      fontSize: 14
    };
  }
}
```

---

## 6. Component Styling

### 6.1. Chart Type Button (Correlation Matrix)

```css
.chart-type-button[data-chart="correlation"] {
  padding: 12px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 160px;
}

.chart-type-button[data-chart="correlation"]:hover {
  border-color: #0066CC;
  background: #f0f7ff;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 102, 204, 0.15);
}

.chart-type-button[data-chart="correlation"]:focus {
  outline: 2px solid #0066CC;
  outline-offset: 2px;
}

.chart-type-button[data-chart="correlation"].active {
  border-color: #0066CC;
  background: #e3f2fd;
  font-weight: 600;
}

.chart-type-button .icon {
  font-size: 28px;
  line-height: 1;
}

.chart-type-button .label {
  font-size: 14px;
  text-align: center;
  line-height: 1.3;
}
```

### 6.2. Column Checkbox List

```css
.correlation-columns-wrapper {
  margin: 20px 0;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.correlation-columns-wrapper label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.column-checkbox-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin: 12px 0;
  padding: 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.column-checkbox {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  min-height: 44px; /* Accessibility */
}

.column-checkbox:hover {
  background: #f5f5f5;
}

.column-checkbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  cursor: pointer;
  accent-color: #0066CC;
}

.column-checkbox input[type="checkbox"]:focus {
  outline: 2px solid #0066CC;
  outline-offset: 2px;
}

.column-checkbox span {
  font-size: 14px;
  color: #333;
  user-select: none;
}

.column-checkbox input[type="checkbox"]:checked + span {
  font-weight: 500;
  color: #0066CC;
}

.helper-text {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: #757575;
  font-style: italic;
}
```

### 6.3. Loading Skeleton

```css
.skeleton-loader {
  width: 100%;
  height: 400px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 20px;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.skeleton-loader::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  to {
    left: 100%;
  }
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
  height: 300px;
}

.skeleton-cell {
  background: #e0e0e0;
  border-radius: 2px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.skeleton-cell:nth-child(odd) {
  animation-delay: 0.1s;
}

.loading-text {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #757575;
  font-weight: 500;
}
```

### 6.4. Sampling Notice

```css
.sampling-notice {
  margin-top: 12px;
  padding: 12px 16px;
  background: #e3f2fd;
  border-left: 4px solid #2196F3;
  border-radius: 4px;
  font-size: 13px;
  color: #0d47a1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sampling-notice .icon {
  font-size: 16px;
  flex-shrink: 0;
}

.sampling-notice .text {
  flex: 1;
  line-height: 1.4;
}
```

### 6.5. Error Display

```css
.chart-error {
  padding: 24px;
  text-align: center;
  background: #fff3e0;
  border: 2px solid #ff9800;
  border-radius: 8px;
  margin: 16px 0;
}

.chart-error .error-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #f57c00;
}

.chart-error .error-title {
  font-size: 16px;
  font-weight: 600;
  color: #e65100;
  margin-bottom: 8px;
}

.chart-error .error-message {
  font-size: 14px;
  color: #d84315;
  line-height: 1.5;
  margin-bottom: 16px;
  white-space: pre-line;
}

.chart-error .retry-button {
  padding: 10px 20px;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.chart-error .retry-button:hover {
  background: #f57c00;
}

.chart-error .retry-button:focus {
  outline: 2px solid #ff9800;
  outline-offset: 2px;
}
```

---

## 7. JavaScript Implementation Guide

### 7.1. State Management Extension

```javascript
// Extend appState.visualization in static/app.js
appState.visualization = {
  // Existing properties
  chartType: null,
  xColumn: null,
  yColumn: null,
  
  // NEW: Correlation matrix specific
  selectedColumns: [],           // Array of selected column names
  correlationMatrix: null,        // Cached correlation data
  correlationStatus: 'idle',      // idle | loading | success | error
  correlationError: null,         // Error message if any
  maxRows: 10000                  // Sampling threshold
};
```

### 7.2. Core Functions

```javascript
// Initialize correlation matrix UI
function initCorrelationMatrix() {
  const button = document.querySelector('[data-chart="correlation"]');
  button.addEventListener('click', handleCorrelationSelection);
}

// Handle correlation matrix chart type selection
function handleCorrelationSelection() {
  appState.visualization.chartType = 'correlation';
  appState.visualization.selectedColumns = [];
  appState.visualization.correlationMatrix = null;
  
  // Hide other chart configurations
  document.getElementById('axis-config').style.display = 'none';
  document.getElementById('chart-type-selector').style.display = 'none';
  
  // Show correlation column selector
  showCorrelationColumnSelector();
}

// Show column selector with smart defaults
function showCorrelationColumnSelector() {
  const wrapper = document.getElementById('correlation-columns-wrapper');
  const columnList = document.getElementById('correlation-column-list');
  
  // Clear existing
  columnList.innerHTML = '';
  
  // Get numeric columns
  const numericColumns = getNumericColumns();
  
  if (numericColumns.length < 2) {
    showChartError('At least 2 numeric columns required for correlation matrix.');
    return;
  }
  
  // Pre-select first 5 columns (smart default)
  const defaultSelection = numericColumns.slice(0, Math.min(5, numericColumns.length));
  appState.visualization.selectedColumns = [...defaultSelection];
  
  // Create checkboxes
  numericColumns.forEach(col => {
    const label = document.createElement('label');
    label.className = 'column-checkbox';
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = col;
    checkbox.checked = defaultSelection.includes(col);
    checkbox.addEventListener('change', handleColumnChange);
    
    const span = document.createElement('span');
    span.textContent = col;
    
    label.appendChild(checkbox);
    label.appendChild(span);
    columnList.appendChild(label);
  });
  
  wrapper.style.display = 'block';
  
  // Auto-generate if valid selection
  if (defaultSelection.length >= 2) {
    debouncedGenerateMatrix();
  }
}

// Get numeric columns from current results
function getNumericColumns() {
  const columnTypes = appState.visualization.columnTypes;
  return Object.keys(columnTypes).filter(col => 
    columnTypes[col] === 'numeric'
  );
}

// Handle column checkbox change
let generateTimeout = null;

function handleColumnChange(event) {
  const column = event.target.value;
  const isChecked = event.target.checked;
  
  if (isChecked) {
    appState.visualization.selectedColumns.push(column);
  } else {
    appState.visualization.selectedColumns = 
      appState.visualization.selectedColumns.filter(c => c !== column);
  }
  
  // Update status message
  updateSelectionStatus();
  
  // Debounced generation
  clearTimeout(generateTimeout);
  
  if (appState.visualization.selectedColumns.length >= 2) {
    generateTimeout = setTimeout(() => {
      generateCorrelationMatrix();
    }, 500); // 500ms debounce
  } else {
    // Clear chart if below minimum
    cleanupChart();
    document.getElementById('chart-container').style.display = 'none';
  }
}

// Update selection status message
function updateSelectionStatus() {
  const count = appState.visualization.selectedColumns.length;
  const statusEl = document.getElementById('column-selection-status');
  
  if (count < 2) {
    statusEl.textContent = `${count} column${count !== 1 ? 's' : ''} selected. Select at least 2 columns.`;
    statusEl.setAttribute('aria-live', 'polite');
  } else if (count > 10) {
    statusEl.textContent = `${count} columns selected. Maximum 10 recommended for readability.`;
    statusEl.setAttribute('aria-live', 'assertive');
  } else {
    statusEl.textContent = `${count} columns selected. Valid selection. Matrix will generate automatically.`;
    statusEl.setAttribute('aria-live', 'polite');
  }
}

// Debounced wrapper
function debouncedGenerateMatrix() {
  clearTimeout(generateTimeout);
  generateTimeout = setTimeout(() => {
    generateCorrelationMatrix();
  }, 500);
}

// Generate correlation matrix
async function generateCorrelationMatrix() {
  const selectedColumns = appState.visualization.selectedColumns;
  const results = appState.currentQuery.results;
  
  // Validation
  if (selectedColumns.length < 2) {
    showChartError('Please select at least 2 columns for correlation analysis.');
    return;
  }
  
  if (selectedColumns.length > 15) {
    showChartError('Maximum 15 columns allowed for correlation matrix.');
    return;
  }
  
  // Update status
  appState.visualization.correlationStatus = 'loading';
  
  // Show loading
  showChartLoading('Calculating correlations...');
  disableCorrelationControls();
  
  try {
    let correlationData;
    
    // Choose calculation strategy
    const rowCount = results.rows.length;
    const colCount = selectedColumns.length;
    
    if (rowCount <= 10000 && colCount <= 5) {
      // Client-side calculation
      correlationData = calculateCorrelationClientSide(
        results.rows,
        selectedColumns
      );
    } else {
      // Backend calculation
      const response = await fetch('/api/correlation-matrix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          columns: selectedColumns,
          rows: results.rows,
          maxRows: appState.visualization.maxRows
        })
      });
      
      correlationData = await response.json();
      
      if (correlationData.status !== 'success') {
        throw new Error(correlationData.message || 'Failed to calculate correlation matrix');
      }
      
      // Show sampling notice if applicable
      if (correlationData.is_sampled) {
        showSamplingNotice(
          correlationData.original_size,
          correlationData.sample_size
        );
      }
    }
    
    // Render the heatmap
    renderCorrelationMatrix(
      correlationData.correlation_matrix,
      selectedColumns
    );
    
    // Update state
    appState.visualization.correlationStatus = 'success';
    appState.visualization.correlationMatrix = correlationData;
    
    // Announce to screen readers
    announceToScreenReader(
      'Correlation matrix generated successfully. Interactive heatmap now displayed.'
    );
    
  } catch (error) {
    console.error('Correlation matrix error:', error);
    appState.visualization.correlationStatus = 'error';
    appState.visualization.correlationError = error.message;
    showChartError(error.message);
  } finally {
    hideChartLoading();
    enableCorrelationControls();
  }
}

// Client-side Pearson correlation
function calculateCorrelationClientSide(rows, columns) {
  const matrix = {};
  
  columns.forEach(col1 => {
    matrix[col1] = {};
    columns.forEach(col2 => {
      if (col1 === col2) {
        matrix[col1][col2] = 1.0;
      } else {
        const x = rows.map(r => r[col1]).filter(v => v != null);
        const y = rows.map(r => r[col2]).filter(v => v != null);
        matrix[col1][col2] = pearsonCorrelation(x, y);
      }
    });
  });
  
  return {
    status: 'success',
    correlation_matrix: matrix,
    columns: columns,
    is_sampled: false
  };
}

// Pearson correlation coefficient
function pearsonCorrelation(x, y) {
  const n = Math.min(x.length, y.length);
  if (n < 2) return 0;
  
  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
  const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
  const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
  
  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
  
  if (denominator === 0) return 0;
  return numerator / denominator;
}

// Render correlation matrix with Plotly
function renderCorrelationMatrix(correlationData, columns) {
  cleanupChart();
  
  // Build Z-matrix
  const zData = columns.map(col1 => 
    columns.map(col2 => correlationData[col1][col2])
  );
  
  // Create annotations
  const annotations = [];
  for (let i = 0; i < columns.length; i++) {
    for (let j = 0; j < columns.length; j++) {
      const value = correlationData[columns[i]][columns[j]];
      annotations.push({
        x: columns[j],
        y: columns[i],
        text: value.toFixed(2),
        showarrow: false,
        font: {
          size: 12,
          color: Math.abs(value) > 0.5 ? 'white' : 'black'
        }
      });
    }
  }
  
  const data = [{
    type: 'heatmap',
    z: zData,
    x: columns,
    y: columns,
    colorscale: 'RdBu',
    reversescale: true,
    zmid: 0,
    zmin: -1,
    zmax: 1,
    colorbar: {
      title: {
        text: 'Correlation<br>Coefficient',
        side: 'right'
      },
      tickmode: 'linear',
      tick0: -1,
      dtick: 0.5
    },
    hovertemplate: 
      '<b>%{y}</b> vs <b>%{x}</b><br>' +
      'Correlation: %{z:.3f}<br>' +
      '<extra></extra>'
  }];
  
  const layout = {
    title: {
      text: 'Correlation Matrix',
      font: { size: 18 }
    },
    xaxis: {
      side: 'bottom',
      tickangle: -45
    },
    yaxis: {
      side: 'left'
    },
    annotations: annotations,
    width: 700,
    height: 700,
    margin: { l: 100, r: 100, t: 100, b: 100 },
    'aria-label': generateChartAriaLabel(correlationData, columns)
  };
  
  const config = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
    displaylogo: false
  };
  
  const container = document.getElementById('chart-container');
  container.style.display = 'block';
  
  Plotly.newPlot(container, data, layout, config);
}

// Generate accessible description
function generateChartAriaLabel(correlationMatrix, columns) {
  let strongestPositive = { value: -1, pair: [] };
  let strongestNegative = { value: 1, pair: [] };
  
  columns.forEach((col1, i) => {
    columns.forEach((col2, j) => {
      if (i < j) {
        const corr = correlationMatrix[col1][col2];
        if (corr > strongestPositive.value) {
          strongestPositive = { value: corr, pair: [col1, col2] };
        }
        if (corr < strongestNegative.value) {
          strongestNegative = { value: corr, pair: [col1, col2] };
        }
      }
    });
  });
  
  return `Correlation matrix heatmap showing relationships between ${columns.length} variables: ${columns.join(', ')}. ` +
    `Strongest positive correlation: ${strongestPositive.pair[0]} and ${strongestPositive.pair[1]} (${strongestPositive.value.toFixed(2)}). ` +
    `Strongest negative correlation: ${strongestNegative.pair[0]} and ${strongestNegative.pair[1]} (${strongestNegative.value.toFixed(2)}).`;
}

// Helper functions
function disableCorrelationControls() {
  document.querySelectorAll('.column-checkbox input').forEach(cb => {
    cb.disabled = true;
  });
}

function enableCorrelationControls() {
  document.querySelectorAll('.column-checkbox input').forEach(cb => {
    cb.disabled = false;
  });
}

function showSamplingNotice(originalSize, sampleSize) {
  const notice = document.getElementById('sampling-notice');
  notice.innerHTML = `
    <span class="icon">ℹ</span>
    <span class="text">Data sampled for performance. Displaying ${sampleSize.toLocaleString()} of ${originalSize.toLocaleString()} rows.</span>
  `;
  notice.style.display = 'flex';
}

function announceToScreenReader(message) {
  const announcer = document.getElementById('screen-reader-announcer');
  announcer.textContent = message;
  setTimeout(() => {
    announcer.textContent = '';
  }, 1000);
}
```

---

## 8. Developer Handoff Checklist

### 8.1. Before Starting Implementation

- [ ] Review architecture document (`docs/correlation-matrix-feature-architecture.md`)
- [ ] Review this frontend specification
- [ ] Understand existing visualization feature implementation
- [ ] Set up development environment
- [ ] Ensure Plotly.js is properly configured

### 8.2. Implementation Checklist

**HTML (static/index.html):**
- [ ] Add correlation matrix button to chart type selector
- [ ] Add correlation-columns-wrapper div
- [ ] Add column-checkbox-list div
- [ ] Add column-selection-status div
- [ ] Add sampling-notice div
- [ ] Add screen-reader-announcer div (if not present)

**CSS (static/styles.css):**
- [ ] Add chart-type-button[data-chart="correlation"] styles
- [ ] Add correlation-columns-wrapper styles
- [ ] Add column-checkbox-list styles
- [ ] Add column-checkbox styles
- [ ] Add skeleton-loader styles
- [ ] Add sampling-notice styles
- [ ] Add responsive styles for mobile/tablet

**JavaScript (static/app.js):**
- [ ] Extend appState.visualization with correlation properties
- [ ] Add initCorrelationMatrix()
- [ ] Add handleCorrelationSelection()
- [ ] Add showCorrelationColumnSelector()
- [ ] Add handleColumnChange()
- [ ] Add generateCorrelationMatrix()
- [ ] Add calculateCorrelationClientSide()
- [ ] Add pearsonCorrelation()
- [ ] Add renderCorrelationMatrix()
- [ ] Add generateChartAriaLabel()
- [ ] Add helper functions

**Accessibility:**
- [ ] Add ARIA labels to all interactive elements
- [ ] Implement keyboard navigation
- [ ] Test with screen reader (NVDA/JAWS)
- [ ] Ensure 4.5:1 color contrast ratios
- [ ] Add focus indicators
- [ ] Test with keyboard only

**Testing:**
- [ ] Test with 2 columns (minimum)
- [ ] Test with 10 columns (maximum recommended)
- [ ] Test with 15 columns (hard limit)
- [ ] Test with dataset < 10K rows (client-side)
- [ ] Test with dataset > 10K rows (backend)
- [ ] Test error scenarios
- [ ] Test on mobile devices
- [ ] Test on tablets
- [ ] Test responsive breakpoints

### 8.3. Quality Assurance

- [ ] All interactions work as specified
- [ ] Smart defaults pre-select first 5 columns
- [ ] Auto-generation works with 500ms debounce
- [ ] Loading states display correctly
- [ ] Error messages are clear and helpful
- [ ] Sampling notice appears when appropriate
- [ ] Chart renders correctly with proper colors
- [ ] Tooltips show detailed information
- [ ] Accessibility requirements met (WCAG 2.1 AA)
- [ ] Responsive design works on all screen sizes
- [ ] Performance meets targets

---

## 9. Future Enhancements

### 9.1. Phase 2 Features

**Interactive Correlation Cells:**
- Click correlation cell → Show scatter plot in modal
- Identify outliers and patterns
- Quick drill-down into relationships

**Statistical Significance:**
- Calculate p-values for each correlation
- Display significance levels (* p<0.05, ** p<0.01, *** p<0.001)
- Filter to show only significant correlations

**Advanced Filtering:**
- Slider to filter by correlation strength (|r| > threshold)
- Sort columns by average correlation
- Hierarchical clustering of variables

### 9.2. Phase 3 Features

**Alternative Correlation Methods:**
- Spearman rank correlation (non-linear relationships)
- Kendall tau correlation
- Toggle between methods

**Export Capabilities:**
- Export as PNG/SVG
- Export as CSV (correlation matrix data)
- Copy to clipboard
- Share via URL

**Custom Color Scales:**
- User-selectable color schemes
- Color-blind friendly alternatives (viridis, plasma)
- Custom color scale editor

---

## 10. Summary

This frontend specification provides comprehensive guidance for implementing the correlation matrix feature. The design prioritizes:

1. **User Experience:** Smart defaults with auto-generation create a frictionless workflow
2. **Accessibility:** WCAG 2.1 Level AA compliance ensures inclusivity
3. **Responsiveness:** Adapts seamlessly to mobile, tablet, and desktop
4. **Performance:** Hybrid calculation strategy handles datasets of any size
5. **Consistency:** Follows existing visualization patterns and design language

**Ready for Development:**
- All wireframes and mockups provided
- Complete CSS specifications included
- JavaScript implementation guide detailed
- Accessibility requirements documented
- Testing checklist prepared

**Questions or Clarifications:**
Contact Sally (UX Expert) for any questions about this specification.

---

**Document Status:** ✅ Ready for Implementation  
**Last Updated:** October 10, 2025  
**Version:** 1.0
