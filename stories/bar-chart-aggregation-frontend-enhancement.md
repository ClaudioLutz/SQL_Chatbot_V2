# User Story: Bar Chart Frontend Enhancement with Metadata Display

**Story ID:** BCA-003  
**Epic:** Bar Chart Aggregation Feature  
**Status:** Complete  
**Priority:** Must Have  
**Estimated Effort:** 2 hours  
**Dependencies:** BCA-002 (API Endpoint Integration)

---

## Story

**As a** frontend developer  
**I want** to update the bar chart rendering to display aggregated data with metadata  
**So that** users see readable charts with transparency about data transformations

---

## Acceptance Criteria

- [ ] `prepareChartDataClientSide()` function updated in `static/app.js` for bar charts
- [ ] Bar charts render aggregated data from backend (50 categories max)
- [ ] Chart title dynamically generated from metadata
- [ ] Metadata annotation displayed below chart showing rows aggregated
- [ ] Warning message shown when categories limited (e.g., "Top 50 of 150")
- [ ] Value formatting implemented (K, M notation for large numbers)
- [ ] Enhanced tooltips with formatted values
- [ ] Bar styling includes borders for definition
- [ ] Y-axis label uses metadata from backend
- [ ] All changes maintain existing UI patterns and responsiveness

---

## Technical Implementation

### File: `static/app.js`

#### Update prepareChartDataClientSide Function

```javascript
function prepareChartDataClientSide({rows, chartType, xColumn, yColumn, bins}) {
    const plotlyData = [];
    const layout = {
        autosize: true,
        margin: {l: 60, r: 40, t: 60, b: 80}
    };
    const config = {responsive: true, displayModeBar: true};
    
    switch (chartType) {
        case 'bar':
            // ===== ENHANCED: Bar chart with aggregated data =====
            // Backend sends aggregated data with 'value' column
            const xValues = rows.map(r => r[xColumn]);
            const yValues = rows.map(r => r.value);
            
            plotlyData.push({
                x: xValues,
                y: yValues,
                type: 'bar',
                marker: {
                    color: '#0066CC',
                    line: {
                        color: '#004d99',
                        width: 1
                    }
                },
                text: yValues.map(v => formatValue(v)),
                textposition: 'outside',
                hovertemplate: 
                    '<b>%{x}</b><br>' +
                    'Value: %{y:,.2f}<br>' +
                    '<extra></extra>'
            });
            
            // Get metadata from backend
            const metadata = appState.visualization.chartData?.metadata || {};
            
            // Set chart title and labels
            layout.title = {
                text: metadata.chart_title || `${yColumn || 'Count'} by ${xColumn}`,
                font: {size: 16}
            };
            layout.xaxis = {
                title: metadata.x_axis_label || xColumn,
                tickangle: -45,
                automargin: true
            };
            layout.yaxis = {
                title: metadata.y_axis_label || 'Value',
                automargin: true
            };
            
            // Add aggregation info annotation
            if (metadata.rows_aggregated) {
                const totalCategories = metadata.total_categories || metadata.categories_shown;
                const aggregationInfo = metadata.aggregation === 'count' 
                    ? `${metadata.rows_aggregated.toLocaleString()} rows aggregated into ${metadata.categories_shown} categories`
                    : `${metadata.aggregation.toUpperCase()}: ${metadata.rows_aggregated.toLocaleString()} rows → ${metadata.categories_shown} categories`;
                
                layout.annotations = [{
                    text: aggregationInfo,
                    xref: 'paper',
                    yref: 'paper',
                    x: 0.5,
                    y: -0.2,
                    xanchor: 'center',
                    yanchor: 'top',
                    showarrow: false,
                    font: {size: 11, color: '#666'}
                }];
                
                // Show warning if categories were limited
                if (metadata.categories_shown < totalCategories) {
                    layout.annotations.push({
                        text: `⚠️ Showing top ${metadata.categories_shown} of ${totalCategories} categories`,
                        xref: 'paper',
                        yref: 'paper',
                        x: 0.5,
                        y: 1.05,
                        xanchor: 'center',
                        showarrow: false,
                        font: {size: 10, color: '#ff6600'}
                    });
                }
            }
            
            break;
            
        case 'scatter':
            // ... existing scatter code unchanged ...
            plotlyData.push({
                x: rows.map(r => r[xColumn]),
                y: rows.map(r => r[yColumn]),
                mode: 'markers',
                type: 'scatter',
                marker: {size: 8, color: '#0066CC'}
            });
            layout.title = `${yColumn} vs ${xColumn}`;
            layout.xaxis = {title: xColumn};
            layout.yaxis = {title: yColumn};
            break;
            
        case 'line':
            // ... existing line code unchanged ...
            plotlyData.push({
                x: rows.map(r => r[xColumn]),
                y: rows.map(r => r[yColumn]),
                type: 'scatter',
                mode: 'lines+markers',
                line: {color: '#0066CC'}
            });
            layout.title = `${yColumn} over ${xColumn}`;
            layout.xaxis = {title: xColumn};
            layout.yaxis = {title: yColumn};
            break;
            
        case 'histogram':
            // ... existing histogram code unchanged ...
            const histogramTrace = {
                x: rows.map(r => r[xColumn]),
                type: 'histogram',
                marker: {color: '#0066CC'}
            };
            
            if (bins !== null && bins !== undefined && bins > 0) {
                histogramTrace.nbinsx = bins;
            }
            
            plotlyData.push(histogramTrace);
            layout.title = `Distribution of ${xColumn}`;
            layout.xaxis = {title: xColumn};
            layout.yaxis = {title: 'Frequency'};
            break;
    }
    
    return {data: plotlyData, layout, config};
}
```

#### Add Value Formatting Function

```javascript
/**
 * Format numeric values with K, M, B notation for readability
 * @param {number} v - Value to format
 * @returns {string} Formatted value string
 */
function formatValue(v) {
    if (v === null || v === undefined) return '';
    
    if (v >= 1000000000) {
        return (v / 1000000000).toFixed(1) + 'B';
    } else if (v >= 1000000) {
        return (v / 1000000).toFixed(1) + 'M';
    } else if (v >= 1000) {
        return (v / 1000).toFixed(1) + 'K';
    } else if (Number.isInteger(v)) {
        return v.toString();
    } else {
        return v.toFixed(2);
    }
}
```

#### Update generateChart Function to Store Metadata

```javascript
async function generateChart() {
    const {chartType, xColumn, yColumn} = appState.visualization;
    const results = appState.currentQuery.results;
    
    if (!results || !results.rows.length) {
        showError('No data available for visualization');
        return;
    }
    
    const maxRows = 10000;
    
    try {
        let chartData;
        
        // For large datasets or bar charts, use backend
        if (results.rows.length > maxRows || chartType === 'bar') {
            const response = await fetch('/api/visualize', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    columns: results.columns,
                    rows: results.rows,
                    chartType,
                    xColumn,
                    yColumn,
                    maxRows
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.message);
            }
            
            // Prepare chart data from backend response
            chartData = prepareChartDataClientSide({
                rows: result.data.rows,
                chartType,
                xColumn,
                yColumn
            });
            
            // Store metadata in state for use in rendering
            appState.visualization.chartData = {
                ...chartData,
                metadata: result.metadata
            };
            
        } else {
            // Small datasets - prepare client-side
            chartData = prepareChartDataClientSide({
                rows: results.rows,
                chartType,
                xColumn,
                yColumn,
                bins: appState.visualization.bins
            });
            
            appState.visualization.chartData = chartData;
        }
        
        // Render the chart
        const chartContainer = document.getElementById('chart-container');
        Plotly.newPlot(
            chartContainer,
            chartData.data,
            chartData.layout,
            chartData.config
        );
        
    } catch (error) {
        console.error('Chart generation error:', error);
        showError(`Failed to generate chart: ${error.message}`);
    }
}
```

---

## Visual Design Specifications

### Bar Styling

```javascript
{
    type: 'bar',
    marker: {
        color: '#0066CC',      // Professional blue
        line: {
            color: '#004d99',   // Darker border
            width: 1            // 1px border for definition
        }
    },
    text: [...],              // Value labels on bars
    textposition: 'outside'   // Position above bars
}
```

### Metadata Annotation (Bottom)

```javascript
{
    text: "1,000,000 rows aggregated into 8 categories",
    xref: 'paper',
    yref: 'paper',
    x: 0.5,                   // Centered horizontally
    y: -0.2,                  // Below chart
    xanchor: 'center',
    yanchor: 'top',
    showarrow: false,
    font: {
        size: 11,
        color: '#666'         // Subtle gray
    }
}
```

### Warning Annotation (Top)

```javascript
{
    text: "⚠️ Showing top 50 of 150 categories",
    xref: 'paper',
    yref: 'paper',
    x: 0.5,                   // Centered horizontally
    y: 1.05,                  // Above chart title
    xanchor: 'center',
    showarrow: false,
    font: {
        size: 10,
        color: '#ff6600'      // Orange warning color
    }
}
```

---

## Testing Requirements

### Manual Testing Checklist

**Test Case 1: Frequency Count (No Y-axis)**
- [ ] Select categorical X-axis (e.g., "Status")
- [ ] Leave Y-axis empty
- [ ] Verify: Chart title says "Frequency Distribution of Status"
- [ ] Verify: Y-axis labeled "Count"
- [ ] Verify: Metadata annotation shows aggregation info
- [ ] Verify: Values formatted with commas

**Test Case 2: Sum Aggregation (With Y-axis)**
- [ ] Select categorical X-axis
- [ ] Select numeric Y-axis (e.g., "Amount")
- [ ] Verify: Chart title says "Total Amount by Status"
- [ ] Verify: Y-axis labeled "Total Amount"
- [ ] Verify: Metadata shows "SUM: X rows → Y categories"
- [ ] Verify: Large values formatted (1.2M, 5.3K, etc.)

**Test Case 3: Category Limit Warning**
- [ ] Query returning 150+ unique categories
- [ ] Generate bar chart
- [ ] Verify: Only 50 bars displayed
- [ ] Verify: Orange warning at top: "⚠️ Showing top 50 of 150"
- [ ] Verify: Bars sorted by value (highest first)

**Test Case 4: Visual Polish**
- [ ] Bar borders visible (1px darker blue)
- [ ] Value labels positioned outside bars
- [ ] Hover tooltips show formatted values
- [ ] Chart responsive to window resize
- [ ] X-axis labels at 45° angle for readability

**Test Case 5: Edge Cases**
- [ ] Single category - renders correctly
- [ ] All unique categories - no aggregation language
- [ ] Very long category names - labels don't overlap
- [ ] Negative values - bars extend below zero
- [ ] Zero values - visible as thin lines

---

## Browser Compatibility

### Target Browsers

- [ ] Chrome 90+ (primary)
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+

### Plotly.js Version

- Using CDN version (already loaded): 2.x
- No additional dependencies needed

---

## Performance Requirements

### Frontend Rendering Targets

| Operation | Target Time | Measurement |
|:----------|:------------|:------------|
| Chart data preparation | <50ms | JavaScript processing |
| Plotly rendering (50 bars) | <200ms | Plotly.newPlot() |
| Window resize re-render | <100ms | Responsive update |
| **Total frontend time** | **<300ms** | User perception |

---

## Accessibility Enhancements

### ARIA Attributes

```javascript
// Add to chart container
document.getElementById('chart-container').setAttribute(
    'aria-label',
    `Bar chart: ${metadata.chart_title}. ${metadata.rows_aggregated} rows aggregated into ${metadata.categories_shown} categories.`
);
```

### Keyboard Navigation

- Plotly handles keyboard navigation by default
- Tab focuses on chart container
- Arrow keys navigate between bars
- Enter shows tooltip for focused bar

---

## State Management Updates

### Store Metadata in App State

```javascript
appState.visualization = {
    // ... existing fields ...
    
    chartData: {
        data: [],           // Plotly data
        layout: {},         // Plotly layout
        config: {},         // Plotly config
        metadata: {         // NEW: Backend metadata
            chart_title: "",
            aggregation: "",
            rows_aggregated: 0,
            categories_shown: 0,
            total_categories: 0
        }
    }
};
```

---

## Error Handling

### Display User-Friendly Errors

```javascript
function showChartError(error) {
    const errorMessages = {
        'INSUFFICIENT_DATA': 'Not enough data for aggregation. At least 2 rows required.',
        'INVALID_METHOD': 'Invalid aggregation method for selected columns.',
        'TOO_MANY_CATEGORIES': 'Too many unique categories. Please filter your data.',
        'NETWORK_ERROR': 'Failed to connect to server. Please try again.',
        'GENERIC': 'Failed to generate chart. Please try again.'
    };
    
    const message = errorMessages[error.code] || errorMessages.GENERIC;
    
    // Display error in chart container
    document.getElementById('chart-container').innerHTML = `
        <div class="chart-error">
            <i class="error-icon">⚠️</i>
            <p>${message}</p>
        </div>
    `;
}
```

---

## Dependencies

- BCA-002: API endpoint must return metadata
- Plotly.js library (already loaded via CDN)
- Existing app state management
- Current visualization UI structure

---

## Backward Compatibility

### Ensure Other Chart Types Unchanged

- [ ] Scatter plot rendering identical
- [ ] Line chart rendering identical
- [ ] Histogram rendering identical
- [ ] Bins parameter still works for histograms
- [ ] Sampling notice still appears for large datasets

---

## Definition of Done

- [ ] `prepareChartDataClientSide()` updated for bar charts
- [ ] `formatValue()` function added and tested
- [ ] `generateChart()` stores metadata correctly
- [ ] All 5 manual test cases pass
- [ ] Visual polish complete (borders, labels, tooltips)
- [ ] Metadata annotations display correctly
- [ ] Warning messages appear when categories limited
- [ ] Browser compatibility verified (Chrome, Firefox, Safari, Edge)
- [ ] Performance targets met (<300ms frontend rendering)
- [ ] No JavaScript console errors
- [ ] Code reviewed by tech lead
- [ ] User documentation updated (if needed)

---

## Notes

- Minimal changes to existing JavaScript structure
- Plotly handles most visual complexity
- Metadata provides full transparency to users
- Value formatting improves readability dramatically
- Warning messages prevent user confusion
- Maintains consistent visual language across all chart types
