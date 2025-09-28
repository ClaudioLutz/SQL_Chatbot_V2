# E1: SQL Safety Layer

## Epic Goal

Establish comprehensive SQL safety and security layer that prevents SQL injection, enforces database access controls, and ensures deterministic query execution before any LLM-generated SQL reaches production data.

## Epic Description

**Existing System Context:**

- Current functionality: Direct SQL execution from GPT-5 generated queries against AdventureWorks database
- Technology stack: FastAPI backend with basic SQL execution, no input validation
- Integration points: GPT-5 SQL generation → direct database execution, no security layer

**Enhancement Details:**

- What's being added/changed: Complete SQL validation middleware with allow-list enforcement, SELECT-only validation, banned keywords filtering, row caps, and query timeouts
- How it integrates: Middleware layer between existing GPT-5 integration and database execution, maintaining API compatibility
- Success criteria: Zero unauthorized SQL operations possible, deterministic results with proper ORDER BY enforcement, comprehensive audit logging

## Stories

1. **Story E1.1:** Allow-List Database Access Control
   - Implement database object allow-list (views/tables) with AdventureWorks-specific configuration
   - Create GRANT SELECT script for least-privilege service account setup
   - Build allow-list validator that rejects queries accessing non-approved objects

2. **Story E1.2:** SQL Statement Validation & Security Controls
   - Develop comprehensive SQL validator rejecting non-SELECT, DDL/DML operations, cross-database references
   - Implement T-SQL compliance enforcement (TOP/OFFSET...FETCH, mandatory ORDER BY with unique tiebreaker validation)
   - Add banned keywords filter and cartesian join detection with row limits

3. **Story E1.3:** Query Resource Controls & Error Handling
   - Implement query timeouts with graceful user messaging and recovery options
   - Add row caps (default 5,000) for non-aggregated results with configurable limits
   - Create structured error taxonomy with user-friendly messages for all validation failures

## Dependencies

**Requires:** E0 (Platform & DevEx) - needs enhanced project structure and database connectivity  
**Blocks:** E2 (LLM→SQL Tooling), E4 (Visualize UI) - SQL safety must be operational before query execution

**Dependency Rationale:** Security layer must be established before any enhanced query processing to ensure no unsafe SQL reaches the database.

## Compatibility Requirements

- [x] Maintain existing FastAPI endpoint response format
- [x] Preserve current query success/failure behavior for valid queries
- [x] Ensure AdventureWorks sample database schema remains unchanged
- [x] Keep existing error handling patterns while enhancing security messaging

## Risk Mitigation

- **Primary Risk:** Over-restrictive validation blocks legitimate queries or breaks existing functionality
- **Mitigation:** Comprehensive testing with existing query patterns, configurable validation rules, detailed error messages with user guidance
- **Rollback Plan:** Validation bypass configuration option for development environments with clear security warnings

## Definition of Done

- [x] All DDL/DML operations completely blocked (INSERT/UPDATE/DELETE/ALTER/DROP rejected)
- [x] Allow-list enforcement operational - only approved AdventureWorks objects accessible
- [x] T-SQL compliance enforced - TOP/OFFSET...FETCH required, ORDER BY mandatory for deterministic results
- [x] Query timeouts and row caps operational with configurable limits
- [x] Comprehensive audit logging implemented for all validation failures
- [x] User-friendly error messages provide actionable guidance for query corrections
- [x] Zero regression in existing valid query functionality

## Integration Verification

- **IV-E1-01:** Existing valid natural language queries continue to execute successfully with enhanced security
- **IV-E1-02:** All unauthorized operations (DROP TABLE, INSERT, etc.) are blocked with clear error messages
- **IV-E1-03:** Queries without ORDER BY when using TOP/OFFSET fail validation with helpful guidance
- **IV-E1-04:** Resource limits (timeouts, row caps) prevent runaway queries while allowing normal operations
- **IV-E1-05:** AdventureWorks-specific allow-list permits expected tables/views while blocking system tables

## Security Acceptance Criteria

**AC-SQL-SAFETY-01:** Attempting "DROP TABLE" operations results in immediate rejection with error "DDL operations not permitted"
**AC-SQL-SAFETY-02:** Queries accessing non-allow-listed objects fail with "Object not in approved schema" error  
**AC-SQL-SAFETY-03:** T-SQL pagination without ORDER BY and unique tiebreaker fails with "ORDER BY with unique column (e.g., PRIMARY KEY) required for deterministic results" guidance
**AC-SQL-SAFETY-04:** Query execution exceeding timeout limits terminates gracefully with retry suggestions
**AC-SQL-SAFETY-05:** Row caps prevent result sets exceeding configured limits with pagination guidance
