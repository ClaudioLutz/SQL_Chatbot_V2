# SQL_Chatbot_V2

## SQL Validator

The SQL Validator provides a security layer that ensures only safe, read-only SELECT operations are permitted against the database. This validator acts as a hard gate - no SQL can be executed without passing validation first.

### Features

- **Read-Only Enforcement**: Only SELECT statements are permitted
- **Allow-List Security**: Only tables/views in the configured allow-list can be queried
- **Deterministic Results**: Queries using TOP or OFFSET/FETCH must include ORDER BY
- **System Protection**: Blocks access to system tables and cross-database references
- **Multi-Statement Prevention**: Blocks semicolon-separated statement batches
- **Comment Stripping**: Removes SQL comments to prevent bypass attempts

### Configuration

Add these environment variables to your `.env` file:

```bash
# SQL Validator Configuration
SQL_ALLOWLIST=Sales.SalesOrderHeader,Sales.SalesOrderDetail,Production.Product,Person.Person
SQL_MAX_ROWS=5000
SQL_TIMEOUT_SECONDS=30
```

### Usage

```python
from app.validation.sql_validator import validate_sql
from app.config import settings

# Validate a SQL query (max_rows parameter is optional with default 5000)
sql = "SELECT TOP 10 * FROM Production.Product ORDER BY ProductID"
result = validate_sql(sql, settings.sql_allowlist_set)  # 2-arg usage
# OR with explicit max_rows:
# result = validate_sql(sql, settings.sql_allowlist_set, settings.sql_max_rows)

if result.ok:
    print("Query is valid!")
    print(f"Referenced objects: {result.objects}")
else:
    print("Query validation failed:")
    for issue in result.issues:
        print(f"  {issue.code}: {issue.message}")
```

## LLM to SQL Generation API

The application provides an API endpoint for converting natural language to T-SQL queries with validation and execution.

### Endpoint: `/api/generate`

**Method**: POST  
**Content-Type**: application/json

**Request Body**:
```json
{
  "prompt": "Show me the top 10 products by price",
  "page": 1,
  "page_size": 20
}
```

**Success Response** (200 OK):
```json
{
  "sql": "SELECT ProductID, Name, ListPrice FROM Production.Product ORDER BY ListPrice DESC, ProductID ASC OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;",
  "columns": [
    {"name": "ProductID", "type": "int"},
    {"name": "Name", "type": "nvarchar"},
    {"name": "ListPrice", "type": "money"}
  ],
  "rows": [
    [776, "Road-650 Black, 58", 782.99],
    [777, "Road-650 Black, 60", 782.99]
  ],
  "page": 1,
  "page_size": 20,
  "meta": {
    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "validated": true,
    "repair_attempts": 0,
    "model": "gpt-4",
    "validation_passed": true,
    "row_count": 2
  }
}
```

**Error Response** (400/422/500):
```json
{
  "error": "SQL_VALIDATION_FAILED",
  "issues": ["ORDER BY required for deterministic results"],
  "meta": {
    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "validation_passed": false,
    "repair_attempts": 3
  }
}
```

### Example Usage

```bash
curl -s -X POST http://localhost:8000/api/generate \
  -H 'Content-Type: application/json' \
  -d '{
        "prompt": "Top 10 products by ListPrice with name and price",
        "page": 1,
        "page_size": 10
      }' | jq .
```

### Common Rejections

The validator will reject queries for these common reasons:

1. **Non-SELECT operations**: `INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.
   ```sql
   -- ❌ REJECTED
   DELETE FROM Production.Product WHERE ProductID = 1
   ```

2. **Tables not in allow-list**:
   ```sql
   -- ❌ REJECTED 
   SELECT * FROM sys.objects
   ```

3. **TOP without ORDER BY**:
   ```sql
   -- ❌ REJECTED
   SELECT TOP 10 * FROM Production.Product
   
   -- ✅ ACCEPTED
   SELECT TOP 10 * FROM Production.Product ORDER BY ProductID
   ```

4. **OFFSET/FETCH without ORDER BY**:
   ```sql
   -- ❌ REJECTED
   SELECT * FROM Production.Product OFFSET 10 ROWS FETCH NEXT 20 ROWS ONLY
   
   -- ✅ ACCEPTED
   SELECT * FROM Production.Product ORDER BY ProductID OFFSET 10 ROWS FETCH NEXT 20 ROWS ONLY
   ```

5. **Cross-database references**:
   ```sql
   -- ❌ REJECTED
   SELECT * FROM master.dbo.spt_values
   ```

6. **Multiple statements**:
   ```sql
   -- ❌ REJECTED
   SELECT * FROM Production.Product; SELECT COUNT(*) FROM Production.Product;
   ```

7. **System objects**:
   ```sql
   -- ❌ REJECTED
   SELECT * FROM sys.tables
   SELECT * FROM information_schema.columns
   ```

8. **Temporary tables**:
   ```sql
   -- ❌ REJECTED
   SELECT * INTO #temp FROM Production.Product
   ```

### Error Codes

- `E_EMPTY_QUERY`: SQL query cannot be empty
- `E_NOT_SELECT`: Only SELECT statements are permitted
- `E_NOT_ALLOWLIST`: Referenced objects not in allow-list
- `E_SYSTEM_OBJECT`: System objects not allowed
- `E_CROSS_DB`: Cross-database references not allowed
- `E_NO_ORDER_BY`: TOP/OFFSET requires ORDER BY for deterministic results
- `E_MULTI_STMT`: Multiple statements not allowed
- `E_TEMP_TABLE`: Temporary tables are not allowed
- `E_DYNAMIC_SQL`: Dynamic SQL execution is not allowed
- `E_PARSE_ERROR`: SQL parsing failed
- `W_CROSS_JOIN`: Warning for CROSS JOIN without WHERE clause
