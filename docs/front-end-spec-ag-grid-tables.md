# Front-End Specification: AG Grid Table Enhancement

**Version:** 1.0  
**Status:** Draft  
**Author:** Sally (UX Expert)  
**Last Updated:** October 1, 2025

---

## 1. Overview

This document provides the detailed front-end design, wireframes, and interaction specifications for replacing the current HTML table rendering with **AG Grid Community Edition** to handle 1M-10M rows with Excel-like performance. This enhancement is a critical component of the SQL Chatbot V2 Enhanced Analysis Feature.

### 1.1. Purpose

Transform the Results tab from basic HTML tables (limited to ~1000 rows before browser performance degrades) to AG Grid with virtual scrolling, enabling smooth interaction with millions of rows while providing Excel-like features users expect.

### 1.2. Goals

- **Performance:** Render 1M-10M rows smoothly with <3 second initial load
- **Excel-like UX:** Sorting, filtering, column resizing, copy/paste
- **Accessibility:** WCAG 2.1 Level AA compliance
- **Responsive:** Works on desktop, tablet, and mobile devices
- **Progressive Enhancement:** Maintains existing functionality while adding new capabilities

### 1.3. Key Design Decisions

| Decision | Choice | Rationale |
|:---------|:-------|:----------|
| Grid Library | AG Grid Community (MIT) | Industry standard, virtual scrolling, free, excellent performance |
| Loading Strategy | CDN | No build step required, maintains vanilla JS architecture |
| Rendering Mode | Client-side | Leverages AG Grid's virtual scrolling, no server pagination needed |
| Default Features | Sort, Filter, Resize, Copy | Most common Excel-like operations |
| Theme | AG Grid Alpine (Light) | Clean, professional, matches existing UI |

---

## 2. Current State Analysis

### 2.1. Current Implementation

**File:** `static/app.js` - `createTable()` function

```javascript
function createTable(columns, rows) {
    let table = '<table><thead><tr>';
    columns.forEach(col => {
        table += `<th>${col}</th>`;
    });
    table += '</tr></thead><tbody>';
    rows.forEach(row => {
        table += '<tr>';
        columns.forEach(col => {
            table += `<td>${row[col] !== null ? row[col] : 'NULL'}</td>`;
        });
        table += '</tr>';
    });
    table += '</tbody></table>';
    return table;
}
```

**Problems:**
- ❌ Renders ALL rows to DOM (browser crashes with >10K rows)
- ❌ No virtual scrolling
- ❌ No sorting or filtering
- ❌ Poor performance with large datasets
- ❌ No column resizing
- ❌ Limited copy/paste functionality

### 2.2. Target Implementation

**AG Grid with:**
- ✅ Virtual scrolling (only renders visible rows)
- ✅ Built-in sorting (multi-column)
- ✅ Built-in filtering (text, number, date)
- ✅ Column resizing and reordering
- ✅ Excel-like copy/paste
- ✅ Smooth scrolling with 1M+ rows
- ✅ Keyboard navigation
- ✅ Accessibility features

---

## 3. Component Breakdown and Wireframes

### 3.1. Results Tab - Current State (Before AG Grid)

```
+------------------------------------------------------------------+
| [ Results ] [ Analysis ] [ Visualizations ]                      |
|------------------------------------------------------------------|
|                                                                  |
| Results:                                                         |
| +--------------------------------------------------------------+ |
| | ProductID | Name           | ListPrice | ModifiedDate       | |
| |-----------|----------------|-----------|--------------------| |
| | 1         | Product A      | 49.99     | 2024-01-01         | |
| | 2         | Product B      | 29.99     | 2024-01-02         | |
| | ...       | ...            | ...       | ...                | |
| +--------------------------------------------------------------+ |
|                                                                  |
| Showing 100 rows                                                 |
+------------------------------------------------------------------+
```

**Issues:**
- Basic HTML table
- No interactivity
- Scrolling entire page
- Performance degrades with >1000 rows

---

### 3.2. Results Tab - Enhanced with AG Grid

```
+------------------------------------------------------------------+
| [ Results ] [ Analysis ] [ Visualizations ]                      |
|------------------------------------------------------------------|
|                                                                  |
| Results: 1,500,000 rows × 12 columns                             |
| +--------------------------------------------------------------+ |
| | [≡] ProductID ▼ | Name ▼        | ListPrice ▼ | ModifiedDate ▼| |
| |     [Filter]    | [Filter]      | [Filter]    | [Filter]     | |
| |-----------------|---------------|-------------|---------------| |
| | 1               | Product A     | 49.99       | 2024-01-01    | |
| | 2               | Product B     | 29.99       | 2024-01-02    | |
| | 3               | Product C     | 39.99       | 2024-01-03    | |
| | ...             | ...           | ...         | ...           | |
| | [Virtual Scroll - Only 50 rows rendered in DOM]               | |
| +--------------------------------------------------------------+ |
| ⚡ Showing rows 1-50 of 1,500,000 | 📋 Copy | 📥 Export CSV      |
+------------------------------------------------------------------+
```

**Features:**
- ✅ Column headers with sort indicators
- ✅ Filter icons in headers
- ✅ Virtual scrolling (smooth with millions of rows)
- ✅ Row count display
- ✅ Action toolbar (copy, export)
- ✅ Resizable columns (drag column borders)

---

### 3.3. AG Grid States

#### 3.3.1. Loading State

```
+------------------------------------------------------------------+
| Results: Loading...                                              |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |                  [ SKELETON LOADER ]                         | |
| |                  Loading data grid...                        | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- Skeleton loader shows grid structure
- Loading message provides context
- Prevents user interaction during load

---

#### 3.3.2. Empty State

```
+------------------------------------------------------------------+
| Results: 0 rows                                                  |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |                  📊 No Results                               | |
| |                  Query returned no data.                     | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- Clear empty state message
- Icon for visual clarity
- Helpful guidance

---

#### 3.3.3. Error State

```
+------------------------------------------------------------------+
| Results: Error                                                   |
| +--------------------------------------------------------------+ |
| |                                                              | |
| |                  ⚠️ Error Loading Data                        | |
| |                  Unable to render table.                     | |
| |                  [Retry]                                     | |
| |                                                              | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- Clear error message
- Retry button for transient errors
- Error details in console for debugging

---

#### 3.3.4. Filtered State

```
+------------------------------------------------------------------+
| Results: 150 of 1,500,000 rows (filtered)                        |
| +--------------------------------------------------------------+ |
| | ProductID ▼ | Name ▼        | ListPrice ▼ | ModifiedDate ▼  | |
| | [Filter: >100] | [Filter: "Pro"] | [Filter]  | [Filter]    | |
| |---------------|---------------|-------------|---------------| |
| | 101           | Product X     | 149.99      | 2024-01-15    | |
| | 102           | Product Y     | 159.99      | 2024-01-16    | |
| | ...           | ...           | ...         | ...           | |
| +--------------------------------------------------------------+ |
| 🔍 Filters active | [Clear All Filters]                          |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- Active filters shown in column headers
- Filter count in status bar
- Clear all filters button
- Filtered row count displayed

---

#### 3.3.5. Sorted State

```
+------------------------------------------------------------------+
| Results: 1,500,000 rows (sorted by ListPrice ↓, Name ↑)         |
| +--------------------------------------------------------------+ |
| | ProductID | Name ▲        | ListPrice ▼ | ModifiedDate      | |
| |-----------|---------------|-------------|-------------------| |
| | 999       | Product Z     | 999.99      | 2024-12-31        | |
| | 888       | Product Y     | 899.99      | 2024-12-30        | |
| | 777       | Product X     | 799.99      | 2024-12-29        | |
| | ...       | ...           | ...         | ...               | |
| +--------------------------------------------------------------+ |
| ↕️ Sorted by 2 columns                                           |
+------------------------------------------------------------------+
```

**Interaction Notes:**
- Sort indicators (▲ ascending, ▼ descending)
- Multi-column sort support
- Sort status in status bar
- Click header to sort, Shift+Click for multi-sort

---

## 4. UI Mockups (ASCII Representation)

### 4.1. Desktop View (1024px+)

```
+---------------------------------------------------------------------------------+
| [Results] [Analysis] [Visualizations]                                           |
|---------------------------------------------------------------------------------|
|                                                                                 |
| Results: 1,500,000 rows × 12 columns                                            |
| +-----------------------------------------------------------------------------+ |
| | [≡] ProductID ▼ | Name ▼          | ListPrice ▼ | Color    | Weight | Size  | |
| |     [🔍]        | [🔍]            | [🔍]        | [🔍]     | [🔍]   | [🔍]  | |
| |-----------------|-----------------|-------------|----------|--------|-------| |
| | 1               | Adjustable Race | 0.00        | NULL     | NULL   | NULL  | |
| | 2               | Bearing Ball    | 0.00        | NULL     | NULL   | NULL  | |
| | 3               | BB Ball Bearing | 0.00        | NULL     | NULL   | NULL  | |
| | 4               | Headset Ball    | 0.00        | NULL     | NULL   | NULL  | |
| | 5               | Blade           | 0.00        | NULL     | NULL   | NULL  | |
| | ...             | ...             | ...         | ...      | ...    | ...   | |
| | [Virtual Scroll - Smooth scrolling through millions of rows]                 | |
| +-----------------------------------------------------------------------------+ |
| ⚡ Rows 1-50 of 1,500,000 | 📋 Copy Selected | 📥 Export CSV | ⚙️ Column Menu  |
+---------------------------------------------------------------------------------+
```

**Features Visible:**
- Column headers with sort/filter icons
- Virtual scrolling viewport
- Status bar with row count
- Action toolbar
- NULL value handling
- Resizable columns (drag borders)

---

### 4.2. Tablet View (768-1023px)

```
+-----------------------------------------------------------------------+
| [Results] [Analysis] [Visualizations]                                 |
|-----------------------------------------------------------------------|
|                                                                       |
| Results: 1,500,000 rows × 12 columns                                  |
| +-----------------------------------------------------------------+   |
| | ProductID ▼ | Name ▼          | ListPrice ▼ | [+6 more]        |   |
| | [🔍]        | [🔍]            | [🔍]        |                  |   |
| |-------------|-----------------|-------------|------------------|   |
| | 1           | Adjustable Race | 0.00        | ...              |   |
| | 2           | Bearing Ball    | 0.00        | ...              |   |
| | 3           | BB Ball Bearing | 0.00        | ...              |   |
| | ...         | ...             | ...         | ...              |   |
| +-----------------------------------------------------------------+   |
| ⚡ Rows 1-30 of 1,500,000 | 📋 Copy | 📥 Export                      |
+-----------------------------------------------------------------------+
```

**Tablet Adaptations:**
- Fewer visible columns (horizontal scroll for more)
- Larger touch targets
- Simplified toolbar
- Optimized for touch interactions

---

### 4.3. Mobile View (< 768px)

```
+----------------------------------+
| [Results] [Analysis] [Viz]       |
|----------------------------------|
|                                  |
| Results: 1.5M rows               |
| +------------------------------+ |
| | ProductID ▼ | Name ▼         | |
| | [🔍]        | [🔍]           | |
| |-------------|----------------| |
| | 1           | Adjustable...  | |
| | 2           | Bearing Ball   | |
| | 3           | BB Ball...     | |
| | ...         | ...            | |
| +------------------------------+ |
| ⚡ 1-20 of 1.5M | 📋 | 📥        |
+----------------------------------+
```

**Mobile Adaptations:**
- Minimal columns visible (2-3)
- Swipe to see more columns
- Compact status bar
- Touch-optimized controls
- Pinch-to-zoom disabled (use column width)

---

## 5. AG Grid Configuration

### 5.1. Core Configuration

```javascript
const gridOptions = {
    // Data
    rowData: [],
    columnDefs: [],
    
    // Performance
    rowBuffer: 10,
    rowModelType: 'clientSide',
    
    // Features
    enableSorting: true,
    enableFilter: true,
    enableColResize: true,
    enableRangeSelection: true,
    
    // UI
    animateRows: false, // Disable for performance with large datasets
    suppressRowHoverHighlight: false,
    suppressCellFocus: false,
    
    // Pagination (disabled - using virtual scrolling)
    pagination: false,
    
    // Accessibility
    suppressMenuHide: false,
    ensureDomOrder: true,
    
    // Callbacks
    onGridReady: onGridReady,
    onFirstDataRendered: onFirstDataRendered,
    onSortChanged: onSortChanged,
    onFilterChanged: onFilterChanged,
    
    // Default column properties
    defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
        minWidth: 100,
        flex: 1,
        cellClass: 'ag-cell-value',
        headerClass: 'ag-header-cell-label'
    }
};
```

### 5.2. Column Definition Strategy

```javascript
function createColumnDefs(columns, rows) {
    return columns.map(col => {
        const columnType = detectColumnType(col, rows);
        
        return {
            field: col,
            headerName: col,
            sortable: true,
            filter: getFilterType(columnType),
            resizable: true,
            minWidth: 100,
            flex: 1,
            
            // Type-specific configuration
            ...(columnType === 'number' && {
                type: 'numericColumn',
                filter: 'agNumberColumnFilter',
                valueFormatter: params => formatNumber(params.value)
            }),
            
            ...(columnType === 'date' && {
                filter: 'agDateColumnFilter',
                valueFormatter: params => formatDate(params.value)
            }),
            
            ...(columnType === 'text' && {
                filter: 'agTextColumnFilter'
            }),
            
            // NULL value handling
            valueGetter: params => {
                const value = params.data[col];
                return value === null || value === undefined ? null : value;
            },
            
            cellRenderer: params => {
                if (params.value === null || params.value === undefined) {
                    return '<span class="null-value">NULL</span>';
                }
                return params.value;
            }
        };
    });
}

function detectColumnType(columnName, rows) {
    // Sample first 100 rows to detect type
    const sample = rows.slice(0, 100);
    const values = sample.map(row => row[columnName]).filter(v => v !== null);
    
    if (values.length === 0) return 'text';
    
    // Check if numeric
    if (values.every(v => typeof v === 'number' || !isNaN(Number(v)))) {
        return 'number';
    }
    
    // Check if date
    if (values.every(v => !isNaN(Date.parse(v)))) {
        return 'date';
    }
    
    return 'text';
}

function getFilterType(columnType) {
    switch (columnType) {
        case 'number': return 'agNumberColumnFilter';
        case 'date': return 'agDateColumnFilter';
        default: return 'agTextColumnFilter';
    }
}
```

### 5.3. Performance Optimization

```javascript
// For datasets > 100K rows
function getOptimizedGridOptions(rowCount) {
    const baseOptions = {...gridOptions};
    
    if (rowCount > 100000) {
        return {
            ...baseOptions,
            animateRows: false,
            suppressRowHoverHighlight: true,
            rowBuffer: 5,
            suppressColumnVirtualisation: false,
            enableCellTextSelection: false,
            suppressCellFocus: true
        };
    }
    
    if (rowCount > 1000000) {
        return {
            ...baseOptions,
            animateRows: false,
            suppressRowHoverHighlight: true,
            rowBuffer: 3,
            suppressColumnVirtualisation: false,
            enableCellTextSelection: false,
            suppressCellFocus: true,
            enableRangeSelection: false // Disable for extreme performance
        };
    }
    
    return baseOptions;
}
```

---

## 6. Implementation Details

### 6.1. HTML Structure

**File:** `static/index.html`

```html
<!-- Add AG Grid CSS in <head> -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/styles/ag-grid.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/styles/ag-theme-alpine.min.css">

<!-- Add AG Grid JS before closing </body> -->
<script src="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/dist/ag-grid-community.min.js"></script>

<!-- Results Tab Content -->
<div id="results-tab" class="tab-content active">
    <div class="results-header">
        <h2>Results: <span id="results-row-count">0 rows</span></h2>
        <div class="results-toolbar">
            <button id="copy-selected-btn" class="toolbar-btn" title="Copy selected rows">
                📋 Copy
            </button>
            <button id="export-csv-btn" class="toolbar-btn" title="Export to CSV">
                📥 Export CSV
            </button>
            <button id="clear-filters-btn" class="toolbar-btn" title="Clear all filters" style="display: none;">
                🔍 Clear Filters
            </button>
        </div>
    </div>
    
    <!-- AG Grid Container -->
    <div id="results-grid" class="ag-theme-alpine" style="height: 600px; width: 100%;"></div>
    
    <!-- Status Bar -->
    <div id="results-status-bar" class="status-bar">
        <span id="status-rows">Rows 0-0 of 0</span>
        <span id="status-filters" style="display: none;">🔍 Filters active</span>
        <span id="status-sort" style="display: none;">↕️ Sorted</span>
    </div>
    
    <!-- Loading State -->
    <div id="results-loading" class="loading-state" style="display: none;">
        <div class="spinner"></div>
        <p>Loading data grid...</p>
    </div>
    
    <!-- Empty State -->
    <div id="results-empty" class="empty-state" style="display: none;">
        <div class="empty-icon">📊</div>
        <h3>No Results</h3>
        <p>Query returned no data.</p>
    </div>
    
    <!-- Error State -->
    <div id="results-error" class="error-state" style="display: none;">
        <div class="error-icon">⚠️</div>
        <h3>Error Loading Data</h3>
        <p id="error-message">Unable to render table.</p>
        <button id="retry-grid-btn" class="retry-btn">Retry</button>
    </div>
</div>
```

### 6.2. CSS Styles

**File:** `static/styles.css`

```css
/* AG Grid Container */
#results-grid {
    height: 600px;
    width: 100%;
    margin-top: 10px;
}

/* Results Header */
.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.results-header h2 {
    margin: 0;
    font-size: 18px;
    color: #333;
}

#results-row-count {
    color: #007bff;
    font-weight: 600;
}

/* Toolbar */
.results-toolbar {
    display: flex;
    gap: 8px;
}

.toolbar-btn {
    padding: 8px 16px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}

.toolbar-btn:hover {
    background: #f8f9fa;
    border-color: #007bff;
}

.toolbar-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Status Bar */
.status-bar {
    display: flex;
    gap: 16px;
    padding: 8px 12px;
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-top: none;
    font-size: 13px;
    color: #666;
}

.status-bar span {
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Loading State */
.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.loading-state .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-state p {
    margin-top: 16px;
    color: #666;
    font-size: 14px;
}

/* Empty State */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.empty-state h3 {
    margin: 0 0 8px 0;
    color: #333;
    font-size: 18px;
}

.empty-state p {
    margin: 0;
    color: #666;
    font-size: 14px;
}

/* Error State */
.error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 4px;
}

.error-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.error-state h3 {
    margin: 0 0 8px 0;
    color: #856404;
    font-size: 18px;
}

.error-state p {
    margin: 0 0 16px 0;
    color: #856404;
    font-size: 14px;
}

.retry-btn {
    padding: 10px 24px;
    border: none;
    border-radius: 4px;
    background: #007bff;
    color: white;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
}

.retry-btn:hover {
    background: #0056b3;
}

/* AG Grid Custom Styles */
.ag-theme-alpine {
    --ag-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    --ag-font-size: 14px;
    --ag-header-height: 48px;
    --ag-row-height: 36px;
    --ag-header-background-color: #f8f9fa;
    --ag-odd-row-background-color: #ffffff;
    --ag-row-hover-color: #f0f7ff;
}

/* NULL value styling */
.null-value {
    color: #999;
    font-style: italic;
}

/* Responsive Design */
@media (max-width: 1023px) {
    #results-grid {
        height: 500px;
    }
    
    .results-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .results-toolbar {
        width: 100%;
        justify-content: flex-start;
    }
}

@media (max-width: 767px) {
    #results-grid {
        height: 400px;
    }
    
    .toolbar-btn {
        padding: 6px 12px;
        font-size: 12px;
    }
    
    .status-bar {
        flex-direction: column;
        gap: 4px;
        font-size: 12px;
    }
}
```

### 6.3. JavaScript Implementation

**File:** `static/app.js`

```javascript
// AG Grid instance
let gridApi = null;
let gridColumnApi = null;

// Replace existing createTable function with AG Grid implementation
function displayResultsWithAGGrid(columns, rows) {
    const gridContainer = document.getElementById('results-grid');
    const loadingState = document.getElementById('results-loading');
    const emptyState = document.getElementById('results-empty');
    const errorState = document.getElementById('results-error');
    const rowCountSpan = document.getElementById('results-row-count');
    
    // Hide all states
    loadingState.style.display = 'none';
    emptyState.style.display = 'none';
    errorState.style.display = 'none';
    gridContainer.style.display = 'none';
    
    // Handle empty results
    if (!rows || rows.length === 0) {
        emptyState.style.display = 'flex';
        rowCountSpan.textContent = '0 rows';
        return;
    }
    
    // Show loading
    loadingState.style.display = 'flex';
    
    try {
        // Destroy existing grid
        if (gridApi) {
            gridApi.destroy();
            gridApi = null;
            gridColumnApi = null;
        }
        
        // Create column definitions
        const columnDefs = createColumnDefs(columns, rows);
        
        // Get optimized grid options based on row count
        const optimizedOptions = getOptimizedGridOptions(rows.length);
        
        // Configure grid
        const gridOptions = {
            ...optimizedOptions,
            columnDefs: columnDefs,
            rowData: rows,
            onGridReady: (params) => {
                gridApi = params.api;
                gridColumnApi = params.columnApi;
                
                // Auto-size columns on first render
                params.api.sizeColumnsToFit();
                
                // Hide loading, show grid
                loadingState.style.display = 'none';
                gridContainer.style.display = 'block';
                
                // Update status bar
                updateStatusBar();
            },
            onSortChanged: updateStatusBar,
            onFilterChanged: updateStatusBar,
            onFirstDataRendered: (params) => {
                console.log(`AG Grid rendered with ${rows.length} rows`);
            }
        };
        
        // Initialize grid
        new agGrid.Grid(gridContainer, gridOptions);
        
        // Update row count
        rowCountSpan.textContent = `${rows.length.toLocaleString()} rows × ${columns.length} columns`;
        
    } catch (error) {
        console.error('Error initializing AG Grid:', error);
        loadingState.style.display = 'none';
        errorState.style.display = 'flex';
        document.getElementById('error-message').textContent = error.message;
    }
}

// Update displayResults to use AG Grid
function displayResults(results) {
    if (results.error) {
        const errorState = document.getElementById('results-error');
        errorState.style.display = 'flex';
        document.getElementById('error-message').textContent = results.error;
    } else {
        displayResultsWithAGGrid(results.columns || [], results.rows || []);
    }
}

// Status bar updates
function updateStatusBar() {
    if (!gridApi) return;
    
    const totalRows = gridApi.getDisplayedRowCount();
    const filteredRows = gridApi.getModel().getRowCount();
    const isFiltered = totalRows !== filteredRows;
    
    // Update row count
    const firstRow = gridApi.getFirstDisplayedRow() + 1;
    const lastRow = gridApi.getLastDisplayedRow() + 1;
    document.getElementById('status-rows').textContent = 
        `Rows ${firstRow.toLocaleString()}-${lastRow.toLocaleString()} of ${totalRows.toLocaleString()}`;
    
    // Update filter status
    const filterStatus = document.getElementById('status-filters');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    if (isFiltered) {
        filterStatus.style.display = 'inline';
        filterStatus.textContent = `🔍 ${filteredRows.toLocaleString()} of ${totalRows.toLocaleString()} rows (filtered)`;
        clearFiltersBtn.style.display = 'inline-block';
    } else {
        filterStatus.style.display = 'none';
        clearFiltersBtn.style.display = 'none';
    }
    
    // Update sort status
    const sortStatus = document.getElementById('status-sort');
    const sortModel = gridApi.getSortModel();
    if (sortModel && sortModel.length > 0) {
        sortStatus.style.display = 'inline';
        const sortDesc = sortModel.map(s => `${s.colId} ${s.sort === 'asc' ? '↑' : '↓'}`).join(', ');
        sortStatus.textContent = `↕️ Sorted by ${sortModel.length} column${sortModel.length > 1 ? 's' : ''}`;
        sortStatus.title = sortDesc;
    } else {
        sortStatus.style.display = 'none';
    }
}

// Toolbar button handlers
document.getElementById('copy-selected-btn').addEventListener('click', () => {
    if (!gridApi) return;
    
    const selectedRows = gridApi.getSelectedRows();
    if (selectedRows.length === 0) {
        // If no selection, copy all visible rows
        gridApi.selectAll();
    }
    
    // Copy to clipboard
    gridApi.copySelectedRowsToClipboard();
    
    // Show feedback
    showNotification('Copied to clipboard', 'success');
});

document.getElementById('export-csv-btn').addEventListener('click', () => {
    if (!gridApi) return;
    
    gridApi.exportDataAsCsv({
        fileName: `query-results-${Date.now()}.csv`,
        columnSeparator: ','
    });
    
    showNotification('CSV exported', 'success');
});

document.getElementById('clear-filters-btn').addEventListener('click', () => {
    if (!gridApi) return;
    
    gridApi.setFilterModel(null);
    showNotification('Filters cleared', 'info');
});

document.getElementById('retry-grid-btn').addEventListener('click', () => {
    // Retry rendering with current data
    const results = appState.currentQuery.results;
    displayResultsWithAGGrid(results.columns, results.rows);
});

// Helper functions
function formatNumber(value) {
    if (value === null || value === undefined) return null;
    if (typeof value === 'number') {
        return value.toLocaleString(undefined, {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        });
    }
    return value;
}

function formatDate(value) {
    if (value === null || value === undefined) return null;
    try {
        const date = new Date(value);
        return date.toLocaleDateString();
    } catch {
        return value;
    }
}

function showNotification(message, type = 'info') {
    // Simple notification (can be enhanced with toast library)
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Optional: Create toast notification
    const toast = document.createElement('div');
    toast.className = `notification-toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
```

---

## 7. Accessibility Specifications

### 7.1. WCAG 2.1 Level AA Compliance

**Compliance Target:** WCAG 2.1 Level AA

#### 7.1.1. Keyboard Navigation

**Tab Sequence:**
1. Results tab button
2. Copy button
3. Export CSV button
4. Clear filters button (when visible)
5. AG Grid (enters grid navigation mode)
6. Within grid: Arrow keys navigate cells, Tab exits grid

**Keyboard Shortcuts:**
- **Tab/Shift+Tab:** Navigate between controls
- **Enter/Space:** Activate buttons
- **Arrow Keys (in grid):** Navigate cells
- **Ctrl+C:** Copy selected cells
- **Ctrl+A:** Select all rows
- **Home/End:** Jump to first/last column
- **Page Up/Down:** Scroll grid
- **Escape:** Exit grid navigation mode

**Focus Management:**
- Visible focus indicator (2px solid outline, color: `#0066CC`)
- Focus trapped within grid during navigation
- Clear focus indicators on all interactive elements
- Skip link: "Skip to grid" for keyboard users

#### 7.1.2. Screen Reader Support

**ARIA Labels:**

```html
<!-- Grid container -->
<div id="results-grid" 
     class="ag-theme-alpine" 
     role="grid"
     aria-label="Query results table with 1,500,000 rows and 12 columns"
     aria-rowcount="1500000"
     aria-colcount="12">
</div>

<!-- Toolbar buttons -->
<button id="copy-selected-btn" 
        aria-label="Copy selected rows to clipboard">
    📋 Copy
</button>

<button id="export-csv-btn" 
        aria-label="Export results to CSV file">
    📥 Export CSV
</button>

<!-- Status bar -->
<div class="status-bar" role="status" aria-live="polite">
    <span id="status-rows">Rows 1-50 of 1,500,000</span>
</div>
```

**Screen Reader Announcements:**
- Grid ready: "Results table loaded with [X] rows and [Y] columns"
- Sort applied: "Sorted by [column] [ascending/descending]"
- Filter applied: "Filtered to [X] rows"
- Copy action: "Copied [X] rows to clipboard"
- Export action: "Exported [X] rows to CSV"

#### 7.1.3. Visual Design Requirements

**Color Contrast:**
- All text: Minimum 4.5:1 contrast ratio
- Interactive elements: Minimum 3:1 contrast against background
- NULL values: Sufficient contrast (#999 on white = 2.85:1, needs improvement to #767676 = 4.54:1)

**Focus Indicators:**
- Visible 2px outline on all focusable elements
- Color: `#0066CC` (sufficient contrast)
- Never remove focus indicators

**Text Sizing:**
- Base font size: 14px (AG Grid default)
- Allow browser text resizing up to 200%
- Use relative units where possible

**Touch Targets:**
- Minimum size: 44x44 pixels (WCAG AAA)
- Column headers: 48px height
- Toolbar buttons: 44px minimum

#### 7.1.4. AG Grid Accessibility Configuration

```javascript
const gridOptions = {
    // ... other options
    
    // Accessibility
    suppressMenuHide: false,
    ensureDomOrder: true,
    enableCellTextSelection: true,
    
    // ARIA labels
    getRowId: (params) => params.data.id || params.node.id,
    
    // Keyboard navigation
    navigateToNextCell: (params) => {
        // Custom navigation logic if needed
        return params.nextCellPosition;
    },
    
    // Screen reader announcements
    onSortChanged: (event) => {
        const sortModel = event.api.getSortModel();
        if (sortModel.length > 0) {
            announceToScreenReader(
                `Sorted by ${sortModel[0].colId} ${sortModel[0].sort}`
            );
        }
    },
    
    onFilterChanged: (event) => {
        const rowCount = event.api.getDisplayedRowCount();
        announceToScreenReader(`Filtered to ${rowCount} rows`);
    }
};

function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => announcement.remove(), 1000);
}
```

### 7.2. Testing Requirements

**Automated Testing:**
- axe-core accessibility audit
- Lighthouse accessibility score (target: 95+)
- Color contrast analyzer

**Manual Testing:**
- Keyboard-only navigation
- Screen reader testing (NVDA, JAWS, VoiceOver)
- High contrast mode (Windows)
- Browser zoom (up to 200%)
- Touch device testing

---

## 8. Responsive Design Strategy

### 8.1. Breakpoints

| Breakpoint | Min Width | Max Width | Grid Height | Visible Columns |
|------------|-----------|-----------|-------------|-----------------|
| Mobile | 320px | 767px | 400px | 2-3 |
| Tablet | 768px | 1023px | 500px | 4-6 |
| Desktop | 1024px | 1439px | 600px | All |
| Wide | 1440px | — | 600px | All |

### 8.2. Responsive Grid Configuration

```javascript
function getResponsiveGridHeight() {
    const width = window.innerWidth;
    
    if (width < 768) return 400;
    if (width < 1024) return 500;
    return 600;
}

function updateGridHeight() {
    const gridContainer = document.getElementById('results-grid');
    gridContainer.style.height = `${getResponsiveGridHeight()}px`;
    
    if (gridApi) {
        gridApi.sizeColumnsToFit();
    }
}

// Update on resize
window.addEventListener('resize', debounce(updateGridHeight, 250));
```

### 8.3. Mobile Optimizations

```javascript
function isMobileDevice() {
    return window.innerWidth < 768;
}

function getMobileGridOptions() {
    if (!isMobileDevice()) return gridOptions;
    
    return {
        ...gridOptions,
        // Disable features for mobile performance
        suppressColumnVirtualisation: true,
        suppressRowHoverHighlight: true,
        enableCellTextSelection: false,
        
        // Larger touch targets
        rowHeight: 44,
        headerHeight: 56,
        
        // Simplified interactions
        enableRangeSelection: false,
        
        // Auto-hide columns on mobile
        columnDefs: gridOptions.columnDefs.map((col, index) => ({
            ...col,
            hide: index > 2 // Show only first 3 columns on mobile
        }))
    };
}
```

---

## 9. Performance Benchmarks

### 9.1. Target Metrics

| Dataset Size | Initial Load | Sort Operation | Filter Operation | Scroll Performance |
|:-------------|:-------------|:---------------|:-----------------|:-------------------|
| 1K rows | <500ms | <100ms | <100ms | 60 FPS |
| 10K rows | <1s | <200ms | <200ms | 60 FPS |
| 100K rows | <2s | <500ms | <500ms | 60 FPS |
| 1M rows | <3s | <1s | <1s | 60 FPS |
| 10M rows | <5s | <2s | <2s | 60 FPS |

### 9.2. Performance Monitoring

```javascript
function measureGridPerformance(operation, fn) {
    const start = performance.now();
    fn();
    const duration = performance.now() - start;
    
    console.log(`[Performance] ${operation}: ${duration.toFixed(2)}ms`);
    
    // Log to analytics if available
    if (window.analytics) {
        analytics.track('grid_performance', {
            operation,
            duration,
            rowCount: gridApi ? gridApi.getDisplayedRowCount() : 0
        });
    }
    
    return duration;
}

// Usage
measureGridPerformance('Grid Initialization', () => {
    displayResultsWithAGGrid(columns, rows);
});
```

### 9.3. Memory Management

```javascript
// Clean up grid when switching tabs or on new query
function cleanupGrid() {
    if (gridApi) {
        gridApi.destroy();
        gridApi = null;
        gridColumnApi = null;
    }
    
    // Clear container
    const gridContainer = document.getElementById('results-grid');
    gridContainer.innerHTML = '';
}

// Call on tab switch or new query
document.querySelectorAll('[data-tab]').forEach(tab => {
    tab.addEventListener('click', (e) => {
        if (e.target.dataset.tab !== 'results') {
            // Don't destroy grid when leaving Results tab
            // Keep it for fast return
        }
    });
});

// Clean up on new query
function handleNewQuery() {
    cleanupGrid();
    // ... rest of query handling
}
```

---

## 10. Migration Plan

### 10.1. Phase 1: Preparation (1 hour)

**Tasks:**
- [ ] Add AG Grid CDN links to HTML
- [ ] Create new CSS styles for grid container
- [ ] Add HTML structure for grid states (loading, empty, error)
- [ ] Test AG Grid loads correctly

### 10.2. Phase 2: Core Implementation (3 hours)

**Tasks:**
- [ ] Implement `displayResultsWithAGGrid()` function
- [ ] Implement `createColumnDefs()` with type detection
- [ ] Implement `getOptimizedGridOptions()` for performance
- [ ] Replace `displayResults()` to use AG Grid
- [ ] Test with small dataset (100 rows)

### 10.3. Phase 3: Features & Polish (2 hours)

**Tasks:**
- [ ] Implement status bar updates
- [ ] Add toolbar button handlers (copy, export, clear filters)
- [ ] Implement responsive design
- [ ] Add accessibility features
- [ ] Test with large dataset (100K rows)

### 10.4. Phase 4: Testing & Optimization (2 hours)

**Tasks:**
- [ ] Performance testing with 1M+ rows
- [ ] Accessibility testing
- [ ] Cross-browser testing
- [ ] Mobile device testing
- [ ] Fix any issues found

### 10.5. Rollback Plan

**If issues arise:**
1. Keep old `createTable()` function as `createTableLegacy()`
2. Add feature flag: `const USE_AG_GRID = true;`
3. Toggle between implementations:

```javascript
function displayResults(results) {
    if (USE_AG_GRID) {
        displayResultsWithAGGrid(results.columns, results.rows);
    } else {
        // Fallback to legacy HTML table
        const resultsOutput = document.getElementById('results-output');
        resultsOutput.innerHTML = createTableLegacy(results.columns, results.rows);
    }
}
```

---

## 11. Testing Strategy

### 11.1. Unit Tests

```javascript
// Test column type detection
describe('detectColumnType', () => {
    test('detects numeric columns', () => {
        const rows = [{val: 1}, {val: 2}, {val: 3}];
        expect(detectColumnType('val', rows)).toBe('number');
    });
    
    test('detects date columns', () => {
        const rows = [{val: '2024-01-01'}, {val: '2024-01-02'}];
        expect(detectColumnType('val', rows)).toBe('date');
    });
    
    test('detects text columns', () => {
        const rows = [{val: 'abc'}, {val: 'def'}];
        expect(detectColumnType('val', rows)).toBe('text');
    });
    
    test('handles NULL values', () => {
        const rows = [{val: null}, {val: 1}, {val: 2}];
        expect(detectColumnType('val', rows)).toBe('number');
    });
});
```

### 11.2. Integration Tests

**Test Scenarios:**
1. **Small Dataset (100 rows):**
   - Grid renders correctly
   - All columns visible
   - Sorting works
   - Filtering works

2. **Large Dataset (100K rows):**
   - Grid renders within 2 seconds
   - Virtual scrolling smooth
   - No browser lag
   - Memory usage acceptable

3. **Huge Dataset (1M rows):**
   - Grid renders within 3 seconds
   - Performance optimizations active
   - Scrolling remains smooth
   - No memory leaks

4. **Edge Cases:**
   - Empty dataset (0 rows)
   - Single row
   - Single column
   - All NULL values
   - Very long column names
   - Special characters in data

### 11.3. Manual Testing Checklist

**Functionality:**
- [ ] Grid renders with data
- [ ] Sorting works (single column)
- [ ] Sorting works (multi-column with Shift+Click)
- [ ] Filtering works (text, number, date)
- [ ] Column resizing works
- [ ] Copy to clipboard works
- [ ] Export to CSV works
- [ ] Clear filters works
- [ ] Status bar updates correctly

**Performance:**
- [ ] 100 rows: <500ms load
- [ ] 10K rows: <1s load
- [ ] 100K rows: <2s load
- [ ] 1M rows: <3s load
- [ ] Smooth scrolling at all sizes
- [ ] No browser freezing

**Accessibility:**
- [ ] Keyboard navigation works
- [ ] Screen reader announces grid
- [ ] Focus indicators visible
- [ ] Color contrast sufficient
- [ ] Works at 200% zoom

**Responsive:**
- [ ] Desktop (1920x1080): All features work
- [ ] Tablet (768x1024): Optimized layout
- [ ] Mobile (375x667): Touch-friendly
- [ ] Landscape orientation works

---

## 12. Future Enhancements

### 12.1. Phase 2 Features

**Advanced Filtering:**
- Custom filter expressions
- Filter presets/templates
- Save filter configurations

**Column Management:**
- Show/hide columns
- Reorder columns (drag & drop)
- Column groups
- Pinned columns (freeze left/right)

**Data Export:**
- Export to Excel (.xlsx)
- Export to JSON
- Export filtered/sorted data only
- Custom export formats

**Cell Editing:**
- Inline cell editing (if needed)
- Bulk edit operations
- Undo/redo support

### 12.2. Phase 3 Features

**Advanced Features:**
- Row grouping
- Aggregation (sum, avg, count)
- Pivot mode
- Master-detail views
- Context menu (right-click)

**Visualization Integration:**
- Quick chart from selected data
- Sparklines in cells
- Conditional formatting
- Heat maps

**Collaboration:**
- Share grid state via URL
- Save custom views
- Collaborative filtering

---

## 13. Documentation

### 13.1. User Guide

**Getting Started:**
1. Execute a SQL query
2. Results appear in AG Grid
3. Click column headers to sort
4. Click filter icon to filter
5. Drag column borders to resize
6. Use toolbar to copy or export

**Keyboard Shortcuts:**
- `Ctrl+C`: Copy selected cells
- `Ctrl+A`: Select all rows
- `Arrow Keys`: Navigate cells
- `Home/End`: Jump to first/last column
- `Page Up/Down`: Scroll grid

**Tips:**
- Hold Shift while clicking headers for multi-column sort
- Double-click column border to auto-size
- Right-click header for column menu
- Use filter icon for advanced filtering

### 13.2. Developer Guide

**Adding AG Grid to New Page:**

```javascript
// 1. Include AG Grid
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/styles/ag-grid.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/styles/ag-theme-alpine.min.css">
<script src="https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.0/dist/ag-grid-community.min.js"></script>

// 2. Create container
<div id="myGrid" class="ag-theme-alpine" style="height: 600px;"></div>

// 3. Initialize grid
const gridOptions = {
    columnDefs: [{field: 'name'}, {field: 'age'}],
    rowData: [{name: 'John', age: 30}]
};
new agGrid.Grid(document.getElementById('myGrid'), gridOptions);
```

---

## 14. Change Log

| Date | Version | Description | Author |
|:-----|:--------|:------------|:-------|
| 2025-10-01 | 1.0 | Initial specification for AG Grid table enhancement | Sally (UX Expert) |

---

## 15. Appendix

### 15.1. AG Grid Resources

- [AG Grid Documentation](https://www.ag-grid.com/javascript-data-grid/)
- [AG Grid Examples](https://www.ag-grid.com/example/)
- [AG Grid API Reference](https://www.ag-grid.com/javascript-data-grid/grid-api/)
- [AG Grid Accessibility](https://www.ag-grid.com/javascript-data-grid/accessibility/)

### 15.2. Performance Tips

1. **Disable animations** for large datasets
2. **Reduce row buffer** for extreme datasets (1M+)
3. **Disable row hover** for better performance
4. **Use column virtualisation** for many columns
5. **Implement pagination** if virtual scrolling isn't enough

### 15.3. Common Issues & Solutions

**Issue:** Grid not rendering
- **Solution:** Check AG Grid script loaded, check console for errors

**Issue:** Slow performance with large dataset
- **Solution:** Use `getOptimizedGridOptions()`, disable animations

**Issue:** Columns too narrow
- **Solution:** Call `gridApi.sizeColumnsToFit()` after data load

**Issue:** Filter not working
- **Solution:** Ensure `filter: true` in column def, check filter type

**Issue:** Copy not working
- **Solution:** Ensure `enableRangeSelection: true` in grid options

---

**End of Document**
