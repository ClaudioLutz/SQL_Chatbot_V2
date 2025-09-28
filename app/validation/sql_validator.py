"""
SQL Validator - Baseline Implementation

Provides comprehensive validation for T-SQL queries to ensure only safe,
read-only SELECT operations are permitted against the database.
"""

import re
import sqlparse
from dataclasses import dataclass
from typing import List, Set, Optional
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, Name


@dataclass
class ValidationIssue:
    """Represents a validation issue found in SQL query."""
    code: str
    message: str


@dataclass
class ValidationResult:
    """Result of SQL validation including any issues found."""
    ok: bool
    issues: List[ValidationIssue]
    objects: Set[str]  # Referenced tables/views (e.g., {"Sales.SalesOrderHeader"})


# Banned SQL operations - comprehensive list
BANNED_OPERATIONS = {
    "INSERT", "UPDATE", "DELETE", "ALTER", "DROP", "CREATE", "MERGE", 
    "TRUNCATE", "EXEC", "EXECUTE", "BULK", "BACKUP", "RESTORE", "GRANT", 
    "REVOKE", "DENY", "DBCC", "SHUTDOWN", "KILL", "CHECKPOINT", "RECONFIGURE"
}

# System tables/views that should be blocked
SYSTEM_OBJECTS = {
    "sys.", "information_schema.", "master.", "msdb.", "model.", "tempdb."
}


def validate_sql(sql: str, allowlist: Set[str], max_rows: int = 5000) -> ValidationResult:
    """
    Validate T-SQL query for security and compliance.
    
    Args:
        sql: The SQL query to validate
        allowlist: Set of allowed table/view names (e.g., {"Sales.Customer", "dbo.Products"})
        max_rows: Maximum number of rows allowed (used for warnings)
    
    Returns:
        ValidationResult with validation status and any issues found
    """
    issues = []
    objects = set()
    
    if not sql or not sql.strip():
        issues.append(ValidationIssue("E_EMPTY_QUERY", "SQL query cannot be empty"))
        return ValidationResult(ok=False, issues=issues, objects=objects)
    
    # Step 1: Normalize and clean the SQL
    normalized_sql = _normalize_sql(sql)
    
    # Step 2: Check for multi-statements (semicolon separation)
    if _has_multiple_statements(normalized_sql):
        issues.append(ValidationIssue(
            "E_MULTI_STMT", 
            "Multiple statements not allowed. Only single SELECT statements are permitted."
        ))
    
    # Step 3: Check for banned operations
    banned_ops = _check_banned_operations(normalized_sql)
    if banned_ops:
        issues.append(ValidationIssue(
            "E_NOT_SELECT", 
            f"Operation not allowed: {', '.join(banned_ops)}. Only SELECT statements are permitted."
        ))
    
    # Step 4: Parse SQL and validate structure
    try:
        parsed = sqlparse.parse(normalized_sql)
        if not parsed:
            issues.append(ValidationIssue("E_PARSE_ERROR", "Unable to parse SQL query"))
            return ValidationResult(ok=False, issues=issues, objects=objects)
            
        statement = parsed[0]
        
        # Step 5: Ensure starts with SELECT (allow WITH CTE → SELECT)
        if not _starts_with_select(statement):
            issues.append(ValidationIssue(
                "E_NOT_SELECT", 
                "Query must start with SELECT statement (WITH CTEs are allowed)"
            ))
        
        # Step 5.5: Check for malformed SELECT statements
        malformed_issues = _check_malformed_syntax(str(statement))
        issues.extend(malformed_issues)
        
        # Step 6: Extract referenced objects and validate against allowlist
        referenced_objects = _extract_table_references(statement)
        objects.update(referenced_objects)
        
        allowlist_violations = _check_allowlist_violations(referenced_objects, allowlist)
        if allowlist_violations:
            issues.append(ValidationIssue(
                "E_NOT_ALLOWLIST", 
                f"Referenced objects not in allowlist: {', '.join(allowlist_violations)}"
            ))
        
        # Step 7: Check for system object references
        system_violations = _check_system_object_violations(referenced_objects)
        if system_violations:
            issues.append(ValidationIssue(
                "E_SYSTEM_OBJECT", 
                f"System objects not allowed: {', '.join(system_violations)}"
            ))
        
        # Step 8: Check for cross-database references
        cross_db_violations = _check_cross_database_references(referenced_objects)
        if cross_db_violations:
            issues.append(ValidationIssue(
                "E_CROSS_DB", 
                f"Cross-database references not allowed: {', '.join(cross_db_violations)}"
            ))
        
        # Step 9: Check deterministic results requirements
        determinism_issues = _check_deterministic_requirements(statement)
        issues.extend(determinism_issues)
        
        # Step 10: Check for potentially dangerous patterns
        danger_issues = _check_dangerous_patterns(normalized_sql)
        issues.extend(danger_issues)
        
    except Exception as e:
        issues.append(ValidationIssue("E_PARSE_ERROR", f"SQL parsing failed: {str(e)}"))
    
    return ValidationResult(ok=len(issues) == 0, issues=issues, objects=objects)


def _normalize_sql(sql: str) -> str:
    """Normalize SQL by removing comments and excess whitespace."""
    # Remove single-line comments (but be careful not to remove -- in strings)
    sql = re.sub(r'--[^\r\n]*', '', sql)
    
    # Remove multi-line comments
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    
    # Normalize whitespace
    sql = ' '.join(sql.split())
    
    return sql.strip()


def _has_multiple_statements(sql: str) -> bool:
    """Check if SQL contains multiple statements separated by semicolons."""
    # Split by semicolon and check if we have more than one non-empty statement
    statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
    return len(statements) > 1


def _check_banned_operations(sql: str) -> Set[str]:
    """Check for banned SQL operations."""
    sql_upper = sql.upper()
    found_banned = set()
    
    for banned_op in BANNED_OPERATIONS:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + re.escape(banned_op) + r'\b'
        if re.search(pattern, sql_upper):
            found_banned.add(banned_op)
    
    return found_banned


def _starts_with_select(statement: Statement) -> bool:
    """Check if statement starts with SELECT (allowing WITH CTEs)."""
    # Get string representation and check first keyword
    sql_text = str(statement).strip().upper()
    
    # Remove leading whitespace and check first keyword
    words = sql_text.split()
    if not words:
        return False
    
    first_word = words[0]
    return first_word in ('SELECT', 'WITH')


def _extract_table_references(statement: Statement) -> Set[str]:
    """Extract table/view references from SQL statement using regex approach."""
    references = set()
    sql_text = str(statement)  # Preserve original case
    
    # Extract CTEs first to exclude them from table validation
    cte_names = _extract_cte_names(sql_text)
    
    # Pattern to match table references after FROM, JOIN keywords
    # Using case-insensitive flag to find matches but preserve original case
    patterns = [
        r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*)?',
        r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*)?',
        r'\bINNER\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*)?',
        r'\bLEFT\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*)?',
        r'\bRIGHT\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*)?',
        r'\bFULL\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*)?',
        r'\bCROSS\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*)?',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, sql_text, re.IGNORECASE)
        for match in matches:
            if match and match.upper() not in ('SELECT', 'WHERE', 'ORDER', 'GROUP', 'HAVING', 'AS', 'ON'):
                # Skip CTE references
                if match.upper() not in {cte.upper() for cte in cte_names}:
                    references.add(match)
    
    return references


def _extract_cte_names(sql_text: str) -> Set[str]:
    """Extract CTE names from WITH clauses."""
    cte_names = set()
    
    # Pattern to match CTE names in WITH clauses
    # Matches: WITH CTE_Name AS (...), CTE_Name2 AS (...)
    cte_pattern = r'\bWITH\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\('
    matches = re.findall(cte_pattern, sql_text, re.IGNORECASE)
    
    for match in matches:
        cte_names.add(match)
    
    # Also handle multiple CTEs: WITH CTE1 AS (...), CTE2 AS (...)
    multi_cte_pattern = r',\s*([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\('
    multi_matches = re.findall(multi_cte_pattern, sql_text, re.IGNORECASE)
    
    for match in multi_matches:
        cte_names.add(match)
    
    return cte_names


def _check_allowlist_violations(references: Set[str], allowlist: Set[str]) -> Set[str]:
    """Check for table references not in allowlist."""
    violations = set()
    
    # Create case-insensitive allowlist for comparison
    allowlist_upper = {item.upper() for item in allowlist}
    
    for ref in references:
        ref_upper = ref.upper()
        
        # Check exact match first (case-insensitive)
        if ref_upper not in allowlist_upper:
            # Check if it might be unqualified (add default schema)
            if '.' not in ref_upper:
                qualified_ref = f"DBO.{ref_upper}"
                if qualified_ref not in allowlist_upper:
                    violations.add(ref)
            else:
                violations.add(ref)
    
    return violations


def _check_system_object_violations(references: Set[str]) -> Set[str]:
    """Check for references to system objects."""
    violations = set()
    
    for ref in references:
        ref_lower = ref.lower()
        for sys_obj in SYSTEM_OBJECTS:
            if ref_lower.startswith(sys_obj):
                violations.add(ref)
                break
    
    return violations


def _check_cross_database_references(references: Set[str]) -> Set[str]:
    """Check for cross-database references (database.schema.table format)."""
    violations = set()
    
    for ref in references:
        # Count dots to detect three-part names (database.schema.table)
        if ref.count('.') >= 2:
            violations.add(ref)
    
    return violations


def _check_deterministic_requirements(statement: Statement) -> List[ValidationIssue]:
    """Check for deterministic result requirements (ORDER BY with TOP/OFFSET)."""
    issues = []
    sql_text = str(statement).upper()
    
    # Check for TOP without ORDER BY
    if re.search(r'\bTOP\s+\d+', sql_text) and 'ORDER BY' not in sql_text:
        issues.append(ValidationIssue(
            "E_NO_ORDER_BY",
            "TOP clause requires ORDER BY for deterministic results"
        ))
    
    # Check for OFFSET/FETCH without ORDER BY
    if ('OFFSET' in sql_text and 'FETCH' in sql_text) and 'ORDER BY' not in sql_text:
        issues.append(ValidationIssue(
            "E_NO_ORDER_BY",
            "OFFSET/FETCH requires ORDER BY for deterministic results"
        ))
    
    return issues


def _check_dangerous_patterns(sql: str) -> List[ValidationIssue]:
    """Check for potentially dangerous SQL patterns."""
    issues = []
    sql_upper = sql.upper()
    
    # Check for temp tables
    if re.search(r'#\w+', sql):
        issues.append(ValidationIssue(
            "E_TEMP_TABLE",
            "Temporary tables are not allowed"
        ))
    
    # Check for dynamic SQL
    if re.search(r'\bEXEC\s*\(', sql_upper):
        issues.append(ValidationIssue(
            "E_DYNAMIC_SQL",
            "Dynamic SQL execution is not allowed"
        ))
    
    # Check for potentially expensive operations
    if re.search(r'\bCROSS\s+JOIN\b', sql_upper) and 'WHERE' not in sql_upper:
        issues.append(ValidationIssue(
            "W_CROSS_JOIN",
            "CROSS JOIN without WHERE clause may be expensive"
        ))
    
    return issues


def _check_malformed_syntax(sql: str) -> List[ValidationIssue]:
    """Check for malformed SQL syntax patterns."""
    issues = []
    sql_upper = sql.upper().strip()
    
    # Check for incomplete SELECT statements
    if sql_upper.startswith('SELECT'):
        # Pattern that catches incomplete SELECT statements
        # SELECT without FROM, or FROM without table name
        if re.match(r'^SELECT\s+(FROM|WHERE|ORDER|GROUP|HAVING)\b', sql_upper):
            issues.append(ValidationIssue(
                "E_PARSE_ERROR",
                "Malformed SELECT statement: missing column list"
            ))
        elif 'FROM' in sql_upper and re.search(r'\bFROM\s+(WHERE|ORDER|GROUP|HAVING|$)', sql_upper):
            issues.append(ValidationIssue(
                "E_PARSE_ERROR", 
                "Malformed SELECT statement: missing table name after FROM"
            ))
        elif re.match(r'^SELECT\s+FROM\s+(WHERE|ORDER|GROUP|HAVING|$)', sql_upper):
            issues.append(ValidationIssue(
                "E_PARSE_ERROR",
                "Malformed SELECT statement: missing column list and table name"
            ))
    
    return issues
