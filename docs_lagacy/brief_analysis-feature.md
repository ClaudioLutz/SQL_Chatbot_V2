# Project Brief: SQL Chatbot - Automatic Data Analysis Feature (POC)

**Author:** Mary, Business Analyst

## 1. Problem Statement

Users can generate SQL queries and view the resulting data tables, but they lack a quick way to understand the basic statistical properties and overall shape of the data they've just queried. To gain initial insights, they would need to manually download the data and analyze it in a separate tool, which is inefficient for rapid exploration.

## 2. Proposed Solution

We will introduce an automatic data analysis feature that appears after a user successfully executes a SQL query. This feature will use the `skimpy` library to generate a concise statistical summary of the query result set. The UI will be updated to include a tabbed interface above the results area with two tabs: "Results" and "Analysis". The "Analysis" tab will display the statistical summary, providing immediate, valuable insights into the data without leaving the application.

## 3. User Value Proposition

This feature will empower users to:
- **Understand Data Instantly:** Get a quick snapshot of the data's characteristics (distributions, data types, cardinality) immediately after running a query.
- **Accelerate Exploration:** Quickly identify patterns, outliers, or data quality issues without switching contexts.
- **Make Faster Decisions:** Use the initial analysis to refine their next query or inform their next steps more efficiently.

## 4. Scope & Requirements (POC)

The goal of this Proof of Concept (POC) is to validate the core functionality and user value with minimal implementation complexity.

**In-Scope Features:**

1.  **Trigger:** The analysis will be generated and displayed automatically after a SQL query returns a non-empty result with at least 2 rows and 1 column.
2.  **Analysis Engine:** The backend will use the `skimpy` library to perform the data analysis.
3.  **Dataset Size Limits:**
    *   **Maximum:** Analysis will only be performed on result sets with ≤50,000 rows to ensure responsive performance.
    *   **Behavior for Large Datasets:** If a query returns >50,000 rows, the Analysis tab will display a message: "Analysis unavailable for datasets exceeding 50,000 rows. Please refine your query for detailed statistics."
4.  **Displayed Statistics:** The analysis page will display the following key information from the `skimpy` report:
    *   **Variable Type Breakdown:** A summary of how many columns belong to each data type (e.g., numeric, categorical, datetime).
    *   **Numeric Distribution Snapshot:** For all numeric columns, show key summary statistics (e.g., mean, standard deviation, min, max, and quartiles).
    *   **Unique Values / Cardinality:** For each column, display the count of unique values.
    *   **Missing Values:** For each column, display the count and percentage of null/missing values for data quality assessment.
5.  **Error Handling:**
    *   If analysis fails for any reason (e.g., unsupported data types, processing errors), the Analysis tab will display: "Analysis could not be generated for this dataset."
    *   The Results tab will always be available regardless of analysis success/failure.
6.  **User Experience:**
    *   The Results tab remains active by default after query execution.
    *   A loading indicator will appear in the Analysis tab while processing (expected <2 seconds for typical datasets).
    *   Users can switch between tabs at any time; analysis persists once generated.

**Out-of-Scope for POC:**

*   Advanced visualizations (histograms, correlation matrices).
*   User-configurable analysis options.
*   Saving or exporting the analysis report.
*   Handling extremely large datasets that could cause performance issues.

## 5. Success Criteria

The POC will be considered successful if:
- A user can run a SQL query and is seamlessly presented with a new page showing the statistical analysis.
- The analysis page correctly displays the three required statistical sections (Variable Types, Numeric Distribution, Cardinality).
- The feature is stable and does not introduce regressions to the existing query functionality.

## 6. Implementation Notes & Constraints

**Backend Implementation:**

*   **Analysis Endpoint:** Create a dedicated POST endpoint `/api/analyze` that accepts the query result DataFrame.
*   **Processing:** Pass the DataFrame directly to `skimpy` in memory (no file I/O for performance).
*   **Row Limit Check:** Before analysis, check row count. If >50,000 rows, return `{"status": "too_large"}` without processing.
*   **Data Format Output:** Extract structured data from skimpy's output and return as JSON:
    ```json
    {
      "status": "success",
      "variable_types": {"numeric": 5, "categorical": 3, "datetime": 1},
      "numeric_stats": [
        {"column": "price", "mean": 45.2, "std": 12.3, "min": 10, "max": 99, "q25": 35, "q50": 44, "q75": 55}
      ],
      "cardinality": [
        {"column": "product_id", "unique_count": 150}
      ],
      "missing_values": [
        {"column": "description", "null_count": 23, "null_percentage": 15.3}
      ]
    }
    ```
*   **Error Handling:** Wrap analysis in try-catch; return `{"status": "error"}` on failure.

**Frontend Implementation:**

*   **Tabbed Interface:** Implement two tabs above results area: "Results" (default active) and "Analysis".
*   **Loading State:** Show spinner/loading indicator in Analysis tab while backend processes (typical: <2 seconds).
*   **Tab Persistence:** Once analysis is generated, persist data on client side when switching tabs.
*   **Display Format:** Render the JSON response as formatted tables/cards for easy readability.

**Technical Constraints:**

*   **Memory:** Skimpy analysis on 50K rows typically uses <100MB RAM; acceptable for POC.
*   **Minimum Dataset:** Analysis requires ≥2 rows to generate meaningful statistics.
*   **Data Type Support:** Skimpy handles standard SQL types; unusual types (JSON, XML, binary) will be shown as "other" in variable types.

## 7. Future Considerations

*   **Async Processing:** For larger datasets (if limit increases), consider async processing with progress updates.
*   **Advanced Visualizations:** Histograms, correlation matrices, distribution plots.
*   **User Configuration:** Allow users to select which statistics to display.
*   **Export Functionality:** Download analysis report as CSV/PDF.
*   **Caching:** Cache analysis results to avoid reprocessing on tab switches.
