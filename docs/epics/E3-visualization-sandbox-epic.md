# E3: Visualization Sandbox

## Epic Goal

Implement secure visualization rendering environment with matplotlib/seaborn support, headless Agg backend, and comprehensive resource controls to generate publication-ready charts while preventing security vulnerabilities and resource exhaustion.

## Epic Description

**Existing System Context:**

- Current functionality: Basic tabular data display only, no visualization capabilities
- Technology stack: FastAPI backend, simple HTML frontend, no Python visualization libraries
- Integration points: SQL results → JSON response → HTML table display

**Enhancement Details:**

- What's being added/changed: Secure Python code execution sandbox with matplotlib/seaborn, PNG chart generation, colorblind-accessible palettes, resource limits, caption generation
- How it integrates: New visualization pipeline between SQL execution and response generation, producing both chart images and metadata
- Success criteria: High-quality accessible charts generated safely within resource constraints, no filesystem/network access, comprehensive error handling

## Stories

1. **Story E3.1:** Headless Matplotlib/Seaborn Foundation
   - Implement headless Agg backend for server-side chart generation (set MPLBACKEND=Agg environment variable or matplotlib.use("Agg") to prevent display crashes)
   - Integrate matplotlib and seaborn with colorblind-accessible default palettes (seaborn colorblind theme)
   - Create chart generation pipeline from SQL result sets to PNG output with descriptive captions

2. **Story E3.2:** Secure Execution Sandbox & Resource Controls
   - Build Python code execution environment with import whitelist (matplotlib, seaborn, pandas, numpy only)
   - Implement comprehensive resource limits: CPU time, memory usage, execution timeout
   - Enforce strict security boundaries: no filesystem access, no network operations, no subprocess execution

3. **Story E3.3:** Chart Intelligence & Export Capabilities
   - Develop automatic chart type selection based on data characteristics (bar, line, scatter, heatmap)
   - Implement PNG export with configurable resolution and quality settings
   - Create descriptive caption generation system explaining chart content and insights for accessibility

## Dependencies

**Requires:** E0 (Platform & DevEx) - needs enhanced project structure and testing framework
**Parallel:** E1 (SQL Safety Layer), E2 (LLM→SQL Tooling) - can develop independently
**Blocks:** E4 (Visualize UI) - UI needs charts from visualization pipeline

**Dependency Rationale:** Visualization capabilities must be operational before UI can display charts, but can develop in parallel with SQL enhancements.

## Compatibility Requirements

- [x] Maintain existing JSON response format while extending with visualization metadata
- [x] Ensure no impact on current tabular data processing pipeline
- [x] Preserve FastAPI static file serving capabilities for PNG delivery
- [x] Keep existing error handling patterns while adding visualization error states

## Risk Mitigation

- **Primary Risk:** Python code execution creates security vulnerabilities or resource exhaustion
- **Mitigation:** Strict sandbox with import whitelist, comprehensive resource monitoring, fail-safe execution with rollback
- **Rollback Plan:** Disable visualization features, fallback to tabular display only with clear user messaging

## Definition of Done

- [x] Headless matplotlib/seaborn operational with Agg backend (no display dependencies)
- [x] Colorblind-accessible palettes default for all chart types (seaborn colorblind theme)
- [x] Secure execution sandbox prevents filesystem, network, and subprocess access
- [x] Resource limits prevent CPU/memory/time exhaustion with graceful error handling
- [x] Automatic chart type selection produces appropriate visualizations for data characteristics
- [x] PNG export generates high-quality charts with configurable settings
- [x] Descriptive captions provide accessibility and insight context for all charts
- [x] Comprehensive error handling covers all sandbox and rendering failure scenarios

## Integration Verification

- **IV-E3-01:** Chart generation completes within resource limits for typical AdventureWorks queries
- **IV-E3-02:** Sandbox security prevents unauthorized file system or network access attempts
- **IV-E3-03:** Matplotlib/seaborn charts render correctly with colorblind-accessible palettes
- **IV-E3-04:** PNG export produces publication-quality output suitable for business presentations
- **IV-E3-05:** Caption generation provides meaningful descriptions for screen reader accessibility

## Visualization Acceptance Criteria

**AC-VIZ-01:** Sales data automatically generates bar charts with seaborn colorblind palette
**AC-VIZ-02:** Time series data produces line charts with appropriate temporal axis formatting
**AC-VIZ-03:** Correlation data generates heatmaps with diverging colorblind-safe color schemes
**AC-VIZ-04:** Attempting file system access fails with "Filesystem access denied in sandbox" error
**AC-VIZ-05:** Charts exceeding 10-second generation time terminate with timeout error and retry guidance

## Performance & Security Targets

- **Chart Generation Time:** ≤ 10 seconds for typical business datasets
- **Memory Usage:** ≤ 512MB per chart generation process
- **CPU Time Limit:** ≤ 10 seconds wall clock time per visualization
- **Security Isolation:** 100% prevention of filesystem, network, and subprocess access
- **Accessibility:** All charts include descriptive captions and use colorblind-accessible palettes

## Chart Type Intelligence

**Data Pattern → Chart Type Mapping:**
- **Single numeric series:** Bar chart with sorted values
- **Time series data:** Line chart with temporal formatting
- **Two numeric variables:** Scatter plot with correlation annotation
- **Categorical breakdowns:** Horizontal bar chart for readability
- **Correlation matrices:** Heatmap with diverging color scheme
- **Geographic data:** If detected, provide guidance for future mapping capabilities
