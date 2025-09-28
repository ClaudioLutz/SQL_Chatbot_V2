# Story 003: LLM to SQL Wrapper

**Epic:** E2 - LLM SQL Tooling Epic  
**Priority:** P1  
**Labels:** `epic:E2`, `type:story`, `prio:P1`  
**Status:** Blocked  
**Blocked By:** Story 002 (SQL Validator Baseline)  
**Board:** SQL Chatbot — Visualisation (Sprint 1)  
**Column:** Backlog  

## Context

Implement the LLM integration layer that converts natural language queries into T-SQL statements using GPT-5. This wrapper must provide comprehensive schema context, enforce T-SQL dialect standards, generate stable pagination patterns, and handle database error repair through iterative prompting.

This component bridges user intent with executable SQL, requiring robust error handling and repair mechanisms to ensure reliable query generation.

## Story

**As a** user of the SQL Chatbot application  
**I want** to convert my natural language questions into valid T-SQL queries  
**So that** I can explore the database without needing to know SQL syntax

## Tasks

### LLM Integration Setup
- [ ] Configure GPT-5 API client with proper authentication
- [ ] Implement async request handling with timeout management
- [ ] Add request/response logging with correlation IDs
- [ ] Set up usage tracking and rate limiting

### Prompt Engineering & Schema Context
- [ ] Create comprehensive T-SQL prompt template
- [ ] Include AdventureWorks schema information in context
- [ ] Provide table/column descriptions and relationships
- [ ] Add example queries demonstrating best practices
- [ ] Include T-SQL dialect-specific patterns and functions

### SQL Generation & Standardization
- [ ] Enforce T-SQL dialect compliance (not MySQL/PostgreSQL)
- [ ] Generate stable pagination using `ORDER BY ... OFFSET ... FETCH NEXT`
- [ ] Ensure deterministic result ordering with unique tiebreakers
- [ ] Handle common T-SQL functions and syntax patterns
- [ ] Validate generated SQL against expected patterns

### Error Handling & Repair Pipeline
- [ ] Capture database execution errors with context
- [ ] Map common DB errors to repair prompts
- [ ] Implement iterative repair attempts (max 3 tries)
- [ ] Track repair success/failure patterns
- [ ] Provide fallback responses for unrepairable queries

### Integration with Validator
- [ ] Pass generated SQL through validation layer (Story 002)
- [ ] Handle validation failures in repair pipeline
- [ ] Log validation results for prompt improvement
- [ ] Ensure seamless integration with existing safety layer

## Acceptance Criteria

1. **SQL Generation:** Natural language queries convert to valid T-SQL statements
2. **Dialect Compliance:** Generated SQL uses T-SQL syntax and functions exclusively
3. **Pagination:** Queries requiring pagination use `ORDER BY ... OFFSET ... FETCH NEXT` pattern
4. **Schema Awareness:** Generated queries reference correct table/column names from AdventureWorks
5. **Error Repair:** Database errors trigger repair attempts with improved prompts
6. **Validation Integration:** All generated SQL passes through safety validator before execution
7. **Performance:** Query generation completes within 5 seconds under normal conditions
8. **Logging:** All LLM interactions logged with correlation IDs for debugging

## Definition of Done

- [ ] Tests green locally and in CI; minimal coverage on new code
- [ ] Config/docs updated (`.env.example`, `README_dev.md`)  
- [ ] Logs include correlation IDs; errors are user-safe (no secrets, no stack dumps)
- [ ] LLM API key management documented and secured
- [ ] Prompt templates versioned and maintainable
- [ ] Error repair patterns documented with examples
- [ ] Performance benchmarks established for typical queries

## Dev Notes

### Technical Requirements
- OpenAI GPT-5 API integration
- Async/await patterns for API calls
- Configurable prompt templates
- Error classification and repair logic
- Integration with existing validator service

### Prompt Template Structure
```
You are a T-SQL expert working with Microsoft SQL Server AdventureWorks database.

SCHEMA CONTEXT:
{schema_information}

REQUIREMENTS:
- Use T-SQL dialect only (not MySQL/PostgreSQL)
- For pagination, use: ORDER BY ... OFFSET ... FETCH NEXT ... ROWS ONLY
- Always include ORDER BY with unique tiebreaker for deterministic results
- Only reference tables in the allowed list: {allowed_tables}

USER QUESTION: {user_question}

Generate a T-SQL query:
```

### Error Repair Mapping
```python
error_patterns = {
    "Invalid column name": "The column '{column}' doesn't exist. Available columns: {available_columns}",
    "Invalid object name": "The table '{table}' doesn't exist. Available tables: {available_tables}",
    "ORDER BY items must appear in SELECT": "Add ORDER BY columns to SELECT clause or use column numbers"
}
```

### AdventureWorks Schema Context
- Include key tables: Products, Categories, Customers, Orders, etc.
- Provide column descriptions and data types
- Document common relationships and foreign keys
- Include example queries for complex scenarios

## Testing

### Unit Tests Required
- LLM API client handles success/failure scenarios
- Prompt template rendering with schema context
- Error pattern matching and repair generation
- SQL dialect validation (T-SQL vs others)
- Pagination pattern detection and correction

### Integration Tests Required
- End-to-end natural language to SQL conversion
- Error repair pipeline with real database errors
- Validation integration with safety layer
- Performance testing under load
- Schema context accuracy with AdventureWorks

### Test Data
```
Natural language queries to test:
- "Show me the top 10 products by sales"
- "Find customers in Seattle who bought bikes"
- "What are the monthly sales trends for 2023?"
- "List all products in the Mountain Bikes category"

Expected error scenarios:
- Invalid column references
- Missing table references  
- Syntax errors requiring repair
- Complex queries needing simplification
```

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Tasks Completed
- [ ] LLM API client implementation
- [ ] Prompt engineering and schema context
- [ ] SQL generation and standardization
- [ ] Error handling and repair pipeline
- [ ] Validator integration
- [ ] Unit tests
- [ ] Integration tests
- [ ] Documentation and examples

### Debug Log References
_To be filled by dev agent with links to specific debug sessions_

### Completion Notes
_To be filled by dev agent with implementation details and decisions_

### File List
_To be filled by dev agent with all new/modified/deleted files_

### Change Log
_To be filled by dev agent with detailed changes made_
