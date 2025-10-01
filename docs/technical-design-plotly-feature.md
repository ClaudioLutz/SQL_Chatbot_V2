# Technical Design: Interactive Visualization Feature

**Version:** 0.1  
**Status:** Draft  
**Author:** Winston (Architect)  

## 1. Overview

This document outlines the technical design and architecture for implementing an interactive visualization feature using Plotly.js within the SQL Chatbot V2 application. It addresses the critical technical decisions identified in the brainstorming session and provides a blueprint for development.

---

## 2. Plotly.js Loading Strategy Evaluation (Technical Spike)

### 2.1. Objective
To determine the optimal strategy for loading the Plotly.js library (~3MB) into the application, balancing initial page load performance, reliability, and maintainability.

### Local Hosting (Bundled)
- **Description:** Include the `plotly.min.js` file within the project's `static` assets and serve it directly from our application.
- **Pros:**
    - **Reliability:** No external dependencies. The library is always available as long as the application is running.
    - **Version Pinning:** Guarantees that the exact version tested during development is used in production, ensuring stability.
    - **Offline Capability:** Works in any environment where the application is accessible.
- **Cons:**
    - **Increased Bundle Size:** Adds ~3MB to the application's assets, which could slow down the initial page load if not managed correctly.
    - **Server Bandwidth:** Consumes our server's bandwidth to serve the library.

### 2.3. Recommended Strategy: Local Hosting with Dynamic Import

The recommended approach is **Local Hosting** combined with **dynamic (lazy) loading**.

- **Implementation:**
    1.  Place the pinned version of `plotly.min.js` in the `static/lib/` directory.
    2.  Do NOT include the `<script>` tag for Plotly in the initial `index.html` load.
    3.  In `static/app.js`, implement a function to dynamically load the script only when the user clicks the "Visualizations" tab for the first time.

- **Rationale:**
    - This hybrid approach provides the reliability and version control of local hosting while mitigating the performance impact.
    - The initial page load remains fast, as the large Plotly.js library is only fetched when explicitly needed.
    - It aligns with the application's "progressive disclosure" philosophy, loading functionality on demand.

```javascript
// Pseudocode for dynamic loading in static/app.js

let plotlyLoaded = false;

function showVisualizationTab() {
    if (!plotlyLoaded) {
        loadScript('static/lib/plotly.min.js', () => {
            plotlyLoaded = true;
            initializeVisualizationUI();
        });
    } else {
        initializeVisualizationUI();
    }
}

function loadScript(src, callback) {
    const script = document.createElement('script');
    script.src = src;
    script.onload = callback;
    document.head.appendChild(script);
}
```

---

## 3. State Management Architecture

### 3.1. Extending the Global `appState`
The existing `appState` object will be extended to manage the state of the visualization tab. This ensures a single source of truth and follows the established pattern.

```javascript
// Proposed extension to appState in static/app.js
const appState = {
    // ... existing states
    visualization: {
        status: "idle", // idle | loading | success | error
        error: null,
        plotlyLoaded: false,
        selectedChartType: null,
        chartConfig: {
            x: null,
            y: null
        },
        chartData: null,
        columnTypes: {} // { "columnName": "numeric" | "categorical" | "datetime" }
    }
};
```

### 3.2. State Transitions
- **`idle`**: The initial state. The UI will show the chart type selector.
- **`loading`**: Triggered when fetching data from the `/api/visualize` endpoint (for large datasets) or during client-side rendering. A skeleton loader will be displayed.
- **`success`**: A chart is successfully rendered. `chartData` is populated.
- **`error`**: An error occurred during data fetching or rendering. The `error` property holds the message to be displayed.

### 3.3. State Persistence
The visualization state will be reset whenever a new SQL query is executed to ensure the chart reflects the latest dataset. State will persist during tab switching within the context of a single query result.

---

## 4. API Contract: `/api/visualize`

### 4.1. Purpose
This new backend endpoint will be responsible for processing large datasets (≥10,001 rows) and returning a sampled or aggregated version suitable for client-side rendering. It will also provide column type information.

### 4.2. Request
- **URL:** `/api/visualize`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "columns": ["col1", "col2", "col3"],
  "rows": [
    { "col1": "A", "col2": 10, "col3": "2025-01-01" },
    { "col1": "B", "col2": 20, "col3": "2025-01-02" }
    // ... up to 50,000 rows
  ],
  "chartType": "bar" // "scatter", "line", "histogram"
}
```

### 4.3. Response (Success)
- **Status Code:** `200 OK`
- **Body:**
```json
{
  "status": "success",
  "column_types": {
    "col1": "categorical",
    "col2": "numeric",
    "col3": "datetime"
  },
  "sampled_data": { // Present only if sampling occurred
    "columns": ["col1", "col2"],
    "rows": [
      { "col1": "A", "col2": 15 },
      { "col1": "B", "col2": 25 }
    ],
    "original_row_count": 50000,
    "sampled_row_count": 10000
  }
}
```

### 4.4. Response (Error)
- **Status Code:** `400 Bad Request` or `500 Internal Server Error`
- **Body:**
```json
{
  "status": "error",
  "message": "A descriptive error message."
}
```

---

## 5. Column Type Detection Algorithm

### 5.1. Objective
To accurately classify each column as `numeric`, `categorical`, or `datetime` to guide chart type compatibility and rendering. This logic will reside on the backend and be executed via the `/api/visualize` endpoint.

### 5.2. Algorithm
For each column, the type will be inferred by examining a sample of the first 100 non-null values.

1.  **Numeric:**
    - A column is classified as `numeric` if > 95% of its sampled values can be cast to a number (integer or float).
2.  **Datetime:**
    - If not numeric, the column is checked against common date/time formats (e.g., `YYYY-MM-DD`, `YYYY-MM-DD HH:MI:SS`, `MM/DD/YYYY`). If > 95% of values match, it's classified as `datetime`.
3.  **Categorical:**
    - If a column is not numeric or datetime, it is classified as `categorical`.
    - A numeric column with low cardinality (e.g., ≤ 10 unique values like product IDs `1, 2, 3`) will also be treated as `categorical`.

This logic will be implemented in a Python utility function on the backend.

---

## 6. Memory Management

### 6.1. Objective
To prevent memory leaks and ensure a smooth user experience, especially when users generate multiple charts or switch between tabs frequently.

### 6.2. Plotly.js Cleanup
- The `Plotly.purge()` method will be called on the chart's container `div` before rendering a new chart or when the user navigates away from the visualization tab. This is critical for releasing the WebGL context and associated memory used by the previous plot.

```javascript
// Pseudocode for chart cleanup in static/app.js
function renderChart(chartData) {
    const chartContainer = document.getElementById('chart-container');
    
    // Purge previous plot to prevent memory leaks
    if (chartContainer.innerHTML !== '') {
        Plotly.purge(chartContainer);
    }
    
    Plotly.newPlot(chartContainer, chartData.data, chartData.layout);
}
```

### 6.3. State Cleanup
- The `appState.visualization` object will be programmatically reset when a new query is initiated to avoid carrying over stale data.

---

## 7. Browser Support

### 7.1. Minimum Browser Versions
To ensure a consistent and functional experience, the visualization feature will officially support the following minimum browser versions:

- **Google Chrome:** Version 90+
- **Mozilla Firefox:** Version 88+
- **Microsoft Edge:** Version 91+
- **Safari:** Version 14+

### 7.2. Rationale
This baseline is selected because these versions provide robust support for:
- **ES6 JavaScript:** Which is used in the existing `app.js`.
- **Fetch API:** For modern asynchronous requests.
- **Plotly.js:** The core rendering library has its own browser compatibility requirements which are met by these versions.

### 7.3. Graceful Degradation
For users on unsupported browsers, the "Visualizations" tab will be disabled, and a message will be displayed indicating the need to upgrade their browser to use the feature. This prevents a broken experience and clearly communicates the requirements.
