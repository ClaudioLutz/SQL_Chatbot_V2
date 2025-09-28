# SQL Chatbot POC — "Visualize" Window Enhancement PRD

## Intro Project Analysis and Context

### Existing Project Overview

**Analysis Source:** IDE-based fresh analysis of loaded project files

**Current Project State:** 
The SQL Chatbot POC is a functional 3-tier web application that enables users to input natural language questions, converts them to SQL via GPT-5, executes against SQL Server (AdventureWorks), and displays tabular results. The current implementation uses FastAPI backend with basic HTML/JS frontend.

### Available Documentation Analysis

**Available Documentation:** ✓ Complete
- ✓ Tech Stack Documentation (Architecture doc available)
- ✓ Source Tree/Architecture (Documented in architecture.md)  
- ✓ API Documentation (FastAPI endpoint structure documented)
- ✓ External API Documentation (GPT-5 integration documented)
- ✓ Technical Debt Documentation (Architecture shows simple POC patterns)
- ⚠️ UX/UI Guidelines (Current basic HTML interface, needs comprehensive UX spec for new tabbed interface)

### Enhancement Scope Definition

**Enhancement Type:** ✓ Major Feature Modification + New Feature Addition + UI/UX Overhaul

**Enhancement Description:** 
Transform the basic SQL chatbot from simple tabular display into a comprehensive "Visualize" window featuring Variant B tabs (Chart | Details | Data), matplotlib/seaborn-generated visualizations with PNG export, robust SQL safety layers, accessibility compliance (WCAG AA), and progressive enhancement patterns.

**Impact Assessment:** ✓ Significant Impact (substantial existing code changes + architectural enhancements required)

### Goals and Background Context

**Goals:**
- Transform POC into production-capable data visualization platform for Data Consumers (management/analysts) and Power Users
- Implement NLQ → GPT-5 → safe SELECT SQL → SQL Server → matplotlib/seaborn visualization pipeline
- Deliver accessible, keyboard-navigable interface with WCAG AA compliance
- Provide multiple data consumption methods: visual charts, detailed SQL inspection, raw data downloads
- Establish robust security layer preventing SQL injection and resource abuse

**Background Context:**
The current SQL Chatbot POC successfully demonstrates natural language to SQL conversion but lacks the visualization and safety features required for management and analyst use. This enhancement addresses the gap between POC demonstration and production deployment by adding comprehensive data visualization, accessibility compliance, and enterprise-grade security measures. The "Visualize" window represents the evolution from simple query results to actionable business insights.

### Change Log

| Change | Date | Version | Description | Author |
|--------|------|---------|-------------|---------|
| Enhancement PRD | 2025-09-28 | 2.0 | Visualization and safety enhancement | BMad PM Agent |

## Requirements

### Functional Requirements

**FR1:** The system shall provide a tabbed interface with three distinct views: Chart (visualization), Details (generated SQL + Python code), and Data (raw results table) following WAI-ARIA Authoring Practices for tabs with roving tabindex and keyboard left/right navigation

**FR2:** The system shall enforce T-SQL syntax compliance, requiring `TOP (n)` or `OFFSET...FETCH` for pagination (forbidding MySQL `LIMIT`) and mandating explicit `ORDER BY` clauses for deterministic results

**FR3:** The system shall implement whitelist-only database access, restricting queries to pre-approved views or tables with rejection of all DDL/DML operations (INSERT/UPDATE/DELETE/ALTER/DROP)

**FR4:** The system shall display progress steps (LLM→SQL→Execute→Render) with ARIA live regions using `role="status"` (polite) for updates and `role="alert"` for critical errors

**FR5:** The system shall generate matplotlib/seaborn visualizations using headless Agg backend with colorblind-accessible palettes (seaborn colorblind or equivalent) and export as PNG with descriptive captions

**FR6:** The system shall provide CSV and PNG download functionality for query results and generated charts

**FR7:** The system shall display both generated SQL query and Python visualization code in Details tab (default collapsed) for transparency and debugging

**FR8:** The system shall implement row caps (default 5,000) for non-aggregated results with explicit `ORDER BY` requirement for any TOP/OFFSET usage

**FR9:** The system shall maintain existing natural language query input functionality while enhancing result presentation

**FR10:** The system shall implement visualization sandbox with CPU/RAM/time resource limits, no filesystem/network access, and only matplotlib/seaborn imports allowed

### Non-Functional Requirements

**NFR1:** Database connections shall use ODBC 18+ with `Encrypt=Yes` by default and configurable `TrustServerCertificate=Yes` option for development with self-signed certificates

**NFR2:** Application service account shall have GRANT SELECT privileges only on allow-listed schema/views with no ownership chaining to sensitive tables

**NFR3:** System shall implement independent timeouts for LLM calls, SQL execution, and rendering with clear user messages and recovery options

**NFR4:** System shall achieve WCAG AA compliance including ≥4.5:1 contrast ratios and Target Size (Minimum) requirements per WCAG 2.2

**NFR5:** System shall implement observability with correlation IDs logging prompt→SQL→execution metrics→render pipeline while redacting PII

**NFR6:** Enhancement must maintain existing query response performance with time-to-first-visual ≤ 10 seconds for small queries

**NFR7:** Interface must support error recovery within ≤ 2 user interaction steps with graceful offline/timeout state handling

### Compatibility Requirements

**CR1:** New tabbed interface must coexist with existing FastAPI backend without breaking current endpoint structure

**CR2:** Database connectivity must maintain compatibility with existing SQL Server 2022 container and ODBC 18 configuration with documented TLS options

**CR3:** AdventureWorks sample database schema must remain unchanged with queries restricted to approved views/tables only

**CR4:** GPT-5 API integration must maintain existing natural language processing capability while adding SQL validation layer

### Acceptance Criteria

**AC-DB-01:** With an empty prompt, UI blocks submission and shows inline guidance

**AC-DB-02:** Given "Top 10 products by sales", the generated SQL compiles on SQL Server and returns ≤10 rows with deterministic order using `ORDER BY`

**AC-SEC-01:** Connecting with ODBC 18+ to a self-signed server fails unless `TrustServerCertificate=Yes` or trusted cert is installed; setting is surfaced in configuration

**AC-A11Y-01:** Tabs are operable via keyboard per WAI-ARIA Authoring Practices; progress updates announced via `aria-live="polite"`; contrast passes WCAG AA validation

**AC-VIS-01:** Charts render via Agg backend; seaborn colorblind palette applied by default; Python code displayed in Details tab

**AC-SQL-01:** SQL validator rejects non-SELECT statements, cross-database references, non-allow-listed objects, missing ORDER BY with TOP/OFFSET, and cartesian joins without limits

### Risk Assessment and Mitigation

**Risk:** TLS failures with ODBC 18 on development environments  
**Mitigation:** Document and expose `Encrypt/TrustServerCertificate` options; provide "dev defaults" .env template

**Risk:** Non-deterministic results without `ORDER BY` clauses  
**Mitigation:** Enforce ORDER BY requirement in SQL validator and include lint tests

**Risk:** Over-broad database access permissions  
**Mitigation:** Ship with curated views that pre-join/filter sensitive columns; GRANT SELECT on views only

**Risk:** Resource exhaustion from visualization rendering  
**Mitigation:** Implement sandbox with CPU/memory/time bounds and headless-only matplotlib execution

## User Interface Enhancement Goals

### Integration with Existing UI

The new tabbed interface will completely replace the existing basic HTML form while maintaining familiar interaction patterns. The enhancement will:

- Preserve the existing question input field and submit functionality as the primary interaction
- Integrate seamlessly with the current FastAPI backend response structure
- Maintain the simple, focused design aesthetic suitable for management/analyst users
- Extend the single-page application approach without requiring complex routing or state management

The tabbed interface will be implemented as a progressive enhancement, ensuring the core functionality remains accessible even with JavaScript disabled (graceful degradation to a basic results page).

### Modified/New Screens and Views

**Enhanced Main Interface (replacing existing index.html):**
- **Input Section:** Retains current natural language query input with enhanced accessibility labels
- **Progress Indicator:** New progressive stepper showing LLM→SQL→Execute→Render stages with ARIA live updates
- **Results Tabbed Interface:** Three-tab layout (Chart | Details | Data) replacing current simple table display
  - **Chart Tab:** Primary visualization with matplotlib/seaborn-generated PNG and descriptive caption
  - **Details Tab:** Collapsible sections showing generated SQL query and Python visualization code
  - **Data Tab:** Enhanced tabular display with CSV download functionality

**No Additional Screens Required:** Enhancement maintains single-page application architecture

### UI Consistency Requirements

**Visual Consistency:**
- Maintain current color scheme and typography while ensuring WCAG AA contrast compliance
- Use consistent button styling and interaction patterns with enhanced focus indicators
- Preserve existing responsive design principles for different screen sizes

**Interaction Consistency:**
- Maintain familiar form submission workflow (question → submit → results)
- Implement consistent error handling and messaging patterns across all tabs
- Ensure keyboard navigation follows logical tab order and expected interaction patterns

**Accessibility Consistency:**
- All new UI elements must follow WAI-ARIA Authoring Practices
- Maintain semantic HTML structure with proper heading hierarchy
- Ensure screen reader compatibility throughout the enhanced interface
- Implement consistent focus management and keyboard interaction patterns

## Technical Constraints and Integration Requirements

### Existing Technology Stack

**Languages:** Python 3.11  
**Frameworks:** FastAPI 0.103.1 (Backend API framework)  
**Database:** MS SQL Server 2019 (SQL Server 2022 container for development)  
**Frontend:** HTML/CSS/JavaScript (latest, basic UI)  
**Database Connectivity:** ODBC 18+ with pyodbc  
**External Dependencies:** GPT-5 API, AdventureWorks sample database  

**Version Constraints:** Must maintain compatibility with existing Python 3.11 and FastAPI 0.103.1 versions

### Integration Approach

**Database Integration Strategy:**
- Extend existing ODBC 18+ connectivity with enhanced security configurations
- Implement SQL validation middleware layer between existing GPT-5 integration and database execution  
- Add allow-list configuration for AdventureWorks schema objects (tables/views)
- Maintain existing connection pooling and error handling patterns

**API Integration Strategy:**
- Preserve existing FastAPI endpoint structure (`/query` or similar)
- Extend response schema to include visualization metadata (chart_url, python_code)
- Add new endpoints for static file serving (PNG charts, CSV downloads)
- Implement streaming response capability for progress updates via Server-Sent Events

**Frontend Integration Strategy:**
- Replace existing static/index.html with enhanced tabbed interface
- Maintain existing static file serving from FastAPI
- Add client-side JavaScript for tab management and accessibility features
- Implement progressive enhancement approach ensuring basic functionality without JavaScript

**Testing Integration Strategy:**
- Extend existing test structure to include SQL validation tests
- Add integration tests for matplotlib/seaborn rendering pipeline
- Implement accessibility testing automation for WCAG AA compliance
- Add database permission testing with least-privilege validation

### Code Organization and Standards

**File Structure Approach:**
```
/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application (existing)
│   ├── services.py          # GPT-5 and DB interaction (existing, extend)
│   ├── validators.py        # New: SQL safety validation
│   ├── visualizer.py        # New: Matplotlib/seaborn rendering
│   └── models.py            # New: Response schemas with visualization
├── static/
│   ├── index.html           # Enhanced tabbed interface (replace existing)
│   ├── styles.css           # Enhanced styling (extend existing)
│   ├── app.js               # New: Tab management and accessibility
│   └── charts/              # New: Generated PNG storage
├── config/
│   ├── database.py          # New: ODBC connection with security options
│   └── allow_list.py        # New: Approved database objects
└── tests/
    ├── test_validators.py   # New: SQL validation tests
    └── test_visualizer.py   # New: Rendering pipeline tests
```

**Naming Conventions:** Maintain existing Python PEP 8 standards with descriptive function/class names
**Coding Standards:** Continue existing FastAPI patterns with type hints and async/await usage
**Documentation Standards:** Extend existing docstring patterns for new modules with security considerations

### Deployment and Operations  

**Build Process Integration:**
- Extend existing requirements.txt with matplotlib, seaborn, and security dependencies
- Add environment validation for visualization dependencies (matplotlib backends)
- Include database schema validation scripts for AdventureWorks allow-list setup

**Deployment Strategy:**
- Maintain existing local development approach with Docker SQL Server container
- Add environment configuration for TLS certificate handling (dev vs production)  
- Implement graceful degradation testing for missing visualization dependencies

**Monitoring and Logging:**
- Extend existing FastAPI logging with correlation IDs for request tracing
- Add performance metrics for visualization rendering pipeline stages
- Implement security event logging for SQL validation failures and resource limit breaches
- Include accessibility audit logging for WCAG compliance monitoring

**Configuration Management:**
- Extend existing environment variable approach for database security settings
- Add configuration validation for allow-list schema objects
- Implement secure storage for GPT-5 API keys with development/production separation
- Add resource limit configuration for visualization sandbox constraints

### Risk Assessment and Mitigation

**Technical Risks:**
- **Matplotlib/Seaborn Dependencies:** Potential conflicts with existing Python environment
- **ODBC 18+ TLS Issues:** Certificate validation failures in development environments  
- **Resource Consumption:** Visualization rendering may impact performance on development machines
- **SQL Server Compatibility:** T-SQL specific syntax requirements may limit portability

**Integration Risks:**
- **FastAPI Response Schema Changes:** New visualization metadata may break existing clients
- **Static File Serving:** Additional PNG/CSV downloads may require routing changes
- **Database Connection Security:** Enhanced ODBC security may break existing development setups
- **Frontend JavaScript Dependencies:** Enhanced accessibility features may conflict with existing minimal approach

**Deployment Risks:**
- **Environment Configuration:** Complex security settings may cause deployment failures
- **Database Permissions:** Least-privilege setup may prevent necessary data access
- **Certificate Management:** TLS configuration differences between development and production
- **Performance Validation:** Visualization rendering timeouts may vary across environments

**Mitigation Strategies:**
- Implement comprehensive environment validation scripts with clear error messaging
- Provide detailed setup documentation with troubleshooting guides for common TLS/ODBC issues
- Add performance monitoring and alerting for visualization rendering pipeline
- Create development environment templates with working configurations for SQL Server container setup

## Epic and Story Structure

### Epic Approach

Based on analysis of logical flow and dependencies, this enhancement should be structured as **multiple tightly-scoped epics** with explicit sequencing rather than one comprehensive epic. This approach aligns with agile guidance to break large initiatives into smaller units and deliver in small batches to improve flow and reduce risk.

**Rationale for Multi-Epic Approach:**
1. **Reduced Batch Size:** Smaller epics correlate with faster lead time and lower failure risk
2. **Clear Dependencies:** Explicit epic sequencing enables parallel development where possible
3. **Faster Feedback:** Each epic delivers measurable value and enables course correction
4. **Risk Isolation:** Technical failures are contained to specific functional areas
5. **Flow Optimization:** Enables DORA-style metrics tracking during POC development

**Epic Structure Decision:** Six targeted epics with clear dependency management and small-batch delivery approach.

### Epic Breakdown and Dependencies

**Dependency Graph:** E0 → (E1, E2, E3) → E4 → E5

**E0. Platform & DevEx (Enabler Epic)**
- Repository scaffolding, FastAPI enhancement, CI/lint/tests, ODBC 18+ connectivity
- *Unblocks all subsequent development work*

**E1. SQL Safety Layer**  
- Allow-list (views/tables), SELECT-only validation, banned keywords, row caps, timeouts
- *Hard security gate before any LLM-generated SQL executes against production data*

**E2. LLM → SQL Tooling**
- GPT-5 prompt strategy, schema hints, error mapping, T-SQL dialect enforcement
- *Prevents dialect drift and ensures deterministic SQL Server pagination patterns*

**E3. Visualization Sandbox**
- Headless matplotlib/seaborn (Agg) renderer, PNG export, resource limits, no FS/network access
- *Security boundary for Python code execution with controlled resource consumption*

**E4. Visualize UI (Variant B)**
- Tabs (Chart|Details|Data), progress stepper, downloads, WAI-ARIA compliance
- *Complete user interface transformation with accessibility and progressive enhancement*

**E5. Observability & A11y QA**
- Stage timings, structured error taxonomy, WCAG AA validation, DORA flow metrics
- *Production readiness validation and delivery health monitoring*

### Epic Sizing and Governance

**Epic Constraints:**
- Each epic completes within 1-2 sprints maximum
- Features within epics fit single iteration/PI cadence
- E0 explicitly treated as enabler epic (architecture runway)
- Flow metrics (lead time, deployment frequency) tracked throughout POC development

**Feature/Story Sequencing Examples:**

**E1 SQL Safety Layer:**
- F1.1: Allow-list resolver (views preferred) + GRANT SELECT script
- F1.2: Validator (reject non-SELECT, missing ORDER BY with TOP/OFFSET, cartesian joins)
- F1.3: Timeouts & row caps with user-friendly error messages

**E4 Visualize UI:**
- F4.1: Tabs with WAI-ARIA keyboard patterns + progress stepper
- F4.2: Chart canvas + Details (SQL/Python) + Data table display  
- F4.3: Downloads (CSV/PNG) + offline/timeout state handling

This multi-epic approach delivers the complete enhancement vision while maintaining agile flow principles and enabling faster feedback cycles throughout development.
