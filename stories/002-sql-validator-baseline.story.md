# Story 002: SQL Validator Baseline

**Epic:** E1 - SQL Safety Layer Epic  
**Priority:** P1  
**Labels:** `epic:E1`, `type:story`, `prio:P1`, `security`  
**Status:** Blocked  
**Blocked By:** Story 001 (Backend Foundation)  
**Board:** SQL Chatbot — Visualisation (Sprint 1)  
**Column:** Backlog  

## Context

Implement a comprehensive SQL validation layer that acts as a security gate before any SQL queries are executed against the database. This validator ensures only safe, read-only SELECT operations are permitted while blocking dangerous DDL/DML operations and enforcing deterministic result patterns.

This is a **hard gate** - no LLM-generated SQL can execute without passing through this validator first. The validator must be bulletproof and provide clear, user-safe error messages when blocking unsafe queries.

## Story

**As a** system administrator and user of the SQL Chatbot  
**I want** a robust SQL validation layer that blocks unsafe queries  
**So that** the database is protected from accidental or malicious modifications while ensuring deterministic, reliable query results

## Tasks

### Core Validation Engine
- [ ] Create SQL parser/validator service class
- [ ] Implement READ-ONLY validation (SELECT statements only)
- [ ] Block all DDL operations (CREATE, ALTER, DROP, TRUNCATE, etc.)
- [ ] Block all DML operations (INSERT, UPDATE, DELETE, MERGE, etc.)
- [ ] Block system/administrative commands (EXEC, BULK INSERT, etc.)

### Allow-List Implementation
- [ ] Create configurable allow-list for permitted tables and views
- [ ] Validate that all referenced objects are in the allow-list
- [ ] Support schema-qualified names (e.g., `dbo.Products`, `Sales.Customer`)
- [ ] Handle table aliases and subqueries correctly

### Deterministic Results Enforcement
- [ ] Detect usage of `TOP` clause without `ORDER BY`
- [ ] Detect `OFFSET/FETCH` without `ORDER BY`
- [ ] Require unique tiebreaker columns in `ORDER BY` (e.g., primary key)
- [ ] Validate `ORDER BY` columns exist in SELECT or underlying tables

### Query Limits & Safety
- [ ] Implement configurable row count limits
- [ ] Add query timeout validation (max execution time)
- [ ] Prevent nested queries beyond reasonable depth
- [ ] Block potentially expensive operations (CROSS JOIN without WHERE, etc.)

### Error Handling & User Experience
- [ ] Generate user-safe error messages (no SQL injection hints)
- [ ] Provide helpful suggestions for fixing common violations
- [ ] Log security violations with correlation IDs
- [ ] Return structured error responses for API consumption

## Acceptance Criteria

1. **Read-Only Enforcement:** Only SELECT statements are permitted; all DDL/DML blocked with clear errors
2. **Allow-List Security:** Only tables/views in the allow-list can be queried
3. **Deterministic Results:** Queries using TOP or OFFSET/FETCH must include ORDER BY with unique tiebreaker
4. **Row Limits:** Configurable maximum row limits enforced (default: 1000 rows)
5. **Timeout Validation:** Query complexity analysis prevents potentially long-running operations
6. **Error Messages:** All error messages are user-safe and provide actionable guidance
7. **Comprehensive Testing:** Unit tests cover all validation scenarios including edge cases
8. **Performance:** Validation completes within 50ms for typical queries

## Definition of Done

- [ ] Tests green locally and in CI; minimal coverage on new code
- [ ] Config/docs updated (`.env.example`, `README_dev.md`)  
- [ ] Logs include correlation IDs; errors are user-safe (no secrets, no stack dumps)
- [ ] Security: comprehensive validation prevents all unsafe SQL patterns
- [ ] Allow-list configuration documented with AdventureWorks examples
- [ ] Performance: validator handles typical queries within 50ms
- [ ] Documentation includes common error scenarios and solutions

## Dev Notes

### Technical Requirements
- Use sqlparse or similar library for SQL parsing
- Configurable allow-lists via environment/config files
- Structured error responses with error codes
- Comprehensive logging for security events

### Allow-List Example Configuration
```json
{
  "allowed_tables": [
    "dbo.Products", 
    "dbo.Categories",
    "Sales.Customer",
    "Sales.SalesOrderHeader",
    "Sales.SalesOrderDetail"
  ],
  "allowed_views": [
    "dbo.vProductAndDescription",
    "Sales.vSalesPersonSalesByFiscalYear"
  ]
}
```

### Error Response Format
```json
{
  "error": "SQL_VALIDATION_FAILED",
  "message": "Query contains blocked DDL operation",
  "details": "CREATE statements are not permitted. Only SELECT queries are allowed.",
  "suggestion": "Rewrite your query using only SELECT statements.",
  "correlation_id": "req_123456"
}
```

### Known Security Considerations
- Prevent SQL injection through parameter validation
- Block comment-based bypass attempts
- Handle Unicode and encoding edge cases
- Validate against common SQL injection patterns

## Testing

### Unit Tests Required
- Valid SELECT queries pass validation
- All DDL operations properly blocked
- All DML operations properly blocked  
- Allow-list enforcement works correctly
- Deterministic result requirements enforced
- Row limit validation functions
- Error message format consistency
- Performance benchmarks for common queries

### Security Tests Required
- SQL injection attempt detection
- Comment-based bypass prevention
- Unicode/encoding attack prevention
- Nested query depth limits
- Cross-join bombing prevention

### Test Data
```sql
-- Valid queries (should pass)
SELECT TOP 100 ProductID, Name FROM dbo.Products ORDER BY ProductID;
SELECT * FROM Sales.Customer WHERE CustomerID = 1;

-- Invalid queries (should be blocked)
DROP TABLE dbo.Products;
INSERT INTO dbo.Products VALUES (1, 'Test');
SELECT TOP 10 * FROM dbo.Products; -- Missing ORDER BY
SELECT * FROM UnauthorizedTable;
```

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Tasks Completed
- [ ] SQL parser/validator service implementation
- [ ] READ-ONLY validation logic
- [ ] Allow-list implementation
- [ ] Deterministic results enforcement
- [ ] Query limits and safety measures
- [ ] Error handling and user experience
- [ ] Comprehensive unit tests
- [ ] Security tests
- [ ] Configuration documentation

### Debug Log References
_To be filled by dev agent with links to specific debug sessions_

### Completion Notes
_To be filled by dev agent with implementation details and decisions_

### File List
_To be filled by dev agent with all new/modified/deleted files_

### Change Log
_To be filled by dev agent with detailed changes made_
