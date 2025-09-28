# E2: LLM → SQL Tooling

## Epic Goal

Enhance GPT-5 integration with robust prompt engineering, schema context awareness, and T-SQL dialect enforcement to generate accurate, safe, and deterministic SQL queries that comply with SQL Server best practices.

## Epic Description

**Existing System Context:**

- Current functionality: Basic GPT-5 API integration for natural language to SQL conversion
- Technology stack: Simple prompt template, no schema context, generic SQL generation
- Integration points: User question → GPT-5 API → raw SQL response → direct execution

**Enhancement Details:**

- What's being added/changed: Advanced prompt engineering with AdventureWorks schema context, T-SQL dialect enforcement, error mapping and recovery, query optimization hints
- How it integrates: Enhanced middleware between user input and SQL safety layer, providing intelligent SQL generation with context awareness
- Success criteria: Higher accuracy SQL generation, consistent T-SQL compliance, intelligent error recovery, reduced user friction

## Stories

1. **Story E2.1:** Advanced Prompt Engineering & Schema Context
   - Develop comprehensive prompt template with AdventureWorks schema awareness (tables, columns, relationships)
   - Implement dynamic schema context injection based on query intent and object references
   - Create query pattern examples library for common business questions (sales, products, customers)

2. **Story E2.2:** T-SQL Dialect Enforcement & Query Optimization
   - Implement T-SQL specific syntax generation (TOP/OFFSET...FETCH instead of LIMIT)
   - Add automatic ORDER BY clause generation for deterministic results
   - Build query optimization hints for AdventureWorks schema (indexes, joins, aggregations)

3. **Story E2.3:** Error Mapping & Recovery Intelligence
   - Create comprehensive error mapping from SQL validation failures to user-friendly guidance
   - Implement query retry logic with automatic corrections for common issues
   - Build contextual help system suggesting query improvements based on error patterns

## Dependencies

**Requires:** E0 (Platform & DevEx), E1 (SQL Safety Layer) - needs secure database connectivity and validation framework
**Blocks:** E4 (Visualize UI) - enhanced SQL generation required for reliable visualization
**Parallel:** E3 (Visualization Sandbox) - can develop independently

**Dependency Rationale:** SQL safety layer must validate generated queries, while enhanced SQL generation improves overall system reliability and user experience.

## Compatibility Requirements

- [x] Maintain existing GPT-5 API integration patterns and authentication
- [x] Preserve current natural language input processing workflow
- [x] Ensure backward compatibility with existing successful query patterns
- [x] Keep response format compatible with current frontend expectations

## Risk Mitigation

- **Primary Risk:** Enhanced prompting changes SQL generation patterns, breaking existing queries
- **Mitigation:** Comprehensive testing with existing query corpus, gradual prompt enhancement deployment, A/B testing capability
- **Rollback Plan:** Simple prompt template fallback configuration with monitoring for generation quality metrics

## Definition of Done

- [x] Advanced prompt template operational with AdventureWorks schema context
- [x] T-SQL compliance enforced - all generated queries use proper SQL Server syntax
- [x] Automatic ORDER BY generation for deterministic results implemented
- [x] Error mapping system provides actionable user guidance for common SQL validation failures  
- [x] Query retry logic reduces user friction for correctable issues
- [x] Schema-aware query generation improves accuracy for complex AdventureWorks relationships
- [x] Comprehensive testing validates no regression in existing successful query patterns

## Integration Verification

- **IV-E2-01:** Enhanced prompting maintains or improves existing query success rates
- **IV-E2-02:** All generated queries comply with T-SQL syntax requirements (no MySQL LIMIT clauses)
- **IV-E2-03:** AdventureWorks schema context improves query accuracy for complex table relationships
- **IV-E2-04:** Error recovery system reduces user retry attempts for common validation failures
- **IV-E2-05:** Query optimization hints improve performance for complex AdventureWorks queries

## LLM Integration Acceptance Criteria

**AC-LLM-01:** Query "Top 10 products by sales" generates T-SQL with "ORDER BY SalesAmount DESC, ProductName" and "TOP (10)"
**AC-LLM-02:** Schema context enables complex queries like "customers with highest orders last quarter" to properly join Customer, Order, and OrderDetail tables
**AC-LLM-03:** Error "missing ORDER BY" triggers automatic retry with corrected query generation
**AC-LLM-04:** Generated queries consistently use AdventureWorks proper table/column names (e.g., SalesOrderHeader not Orders)
**AC-LLM-05:** Query complexity automatically optimizes for AdventureWorks indexes and common access patterns

## Performance Targets

- **LLM Response Time:** ≤ 3 seconds for typical business queries
- **Query Accuracy:** ≥ 85% success rate for AdventureWorks business questions
- **Error Recovery:** ≤ 2 user interactions required for query refinement
- **Schema Context:** 100% coverage of AdventureWorks primary business entities (Sales, Products, Customers)
