"""
Test SQL Validator - Comprehensive test suite

Tests all validation rules and edge cases for the SQL validator.
"""

import pytest
from app.validation.sql_validator import validate_sql, ValidationIssue, ValidationResult


class TestSQLValidator:
    """Test cases for SQL validator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {
            "Sales.SalesOrderHeader",
            "Sales.SalesOrderDetail", 
            "Production.Product",
            "Person.Person",
            "dbo.Products",
            "dbo.Categories"
        }
    
    def test_empty_query(self):
        """Test validation of empty queries."""
        result = validate_sql("", self.allowlist)
        assert not result.ok
        assert len(result.issues) == 1
        assert result.issues[0].code == "E_EMPTY_QUERY"
    
    def test_whitespace_only_query(self):
        """Test validation of whitespace-only queries."""
        result = validate_sql("   \n\t  ", self.allowlist)
        assert not result.ok
        assert len(result.issues) == 1
        assert result.issues[0].code == "E_EMPTY_QUERY"


class TestValidSelectQueries:
    """Test valid SELECT queries that should pass validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {
            "Sales.SalesOrderHeader",
            "Sales.SalesOrderDetail", 
            "Production.Product",
            "Person.Person",
            "dbo.Products",
            "dbo.Categories"
        }
    
    def test_simple_select_with_order_by(self):
        """Test simple SELECT with ORDER BY - should pass."""
        sql = "SELECT TOP (10) ProductID, Name FROM Production.Product ORDER BY ProductID"
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0
        assert "Production.Product" in result.objects
    
    def test_select_with_offset_fetch(self):
        """Test SELECT with OFFSET/FETCH and ORDER BY - should pass."""
        sql = """
        SELECT soh.SalesOrderID, soh.OrderDate 
        FROM Sales.SalesOrderHeader soh 
        ORDER BY soh.SalesOrderID 
        OFFSET 0 ROWS FETCH NEXT 25 ROWS ONLY
        """
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0
        assert "Sales.SalesOrderHeader" in result.objects
    
    def test_select_with_joins(self):
        """Test SELECT with JOINs - should pass."""
        sql = """
        SELECT p.ProductID, p.Name, c.CategoryName
        FROM dbo.Products p
        INNER JOIN dbo.Categories c ON p.CategoryID = c.CategoryID
        ORDER BY p.ProductID
        """
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0
        assert "dbo.Products" in result.objects
        assert "dbo.Categories" in result.objects
    
    def test_select_with_where_clause(self):
        """Test SELECT with WHERE clause - should pass."""
        sql = """
        SELECT ProductID, Name 
        FROM Production.Product 
        WHERE ProductID > 100 
        ORDER BY ProductID
        """
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0
        assert "Production.Product" in result.objects


class TestBannedOperations:
    """Test that banned SQL operations are properly rejected."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"dbo.TestTable"}
    
    @pytest.mark.parametrize("operation,sql", [
        ("DELETE", "DELETE FROM dbo.TestTable WHERE id = 1"),
        ("INSERT", "INSERT INTO dbo.TestTable (name) VALUES ('test')"),
        ("UPDATE", "UPDATE dbo.TestTable SET name = 'test' WHERE id = 1"),
        ("DROP", "DROP TABLE dbo.TestTable"),
        ("CREATE", "CREATE TABLE test (id int)"),
        ("ALTER", "ALTER TABLE dbo.TestTable ADD column1 int"),
        ("TRUNCATE", "TRUNCATE TABLE dbo.TestTable"),
        ("MERGE", "MERGE dbo.TestTable AS target USING source ON target.id = source.id"),
        ("EXEC", "EXEC sp_help 'dbo.TestTable'"),
        ("EXECUTE", "EXECUTE sp_help 'dbo.TestTable'")
    ])
    def test_banned_operations_rejected(self, operation, sql):
        """Test that banned operations are rejected."""
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_NOT_SELECT" for issue in result.issues)
        assert operation in str(result.issues)


class TestAllowListValidation:
    """Test allowlist validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {
            "Sales.SalesOrderHeader",
            "Production.Product"
        }
    
    def test_table_not_in_allowlist(self):
        """Test rejection of table not in allowlist."""
        sql = "SELECT * FROM sys.objects"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_NOT_ALLOWLIST" for issue in result.issues)
        assert "sys.objects" in str(result.issues)
    
    def test_multiple_violations(self):
        """Test multiple allowlist violations."""
        sql = """
        SELECT o.name, t.name 
        FROM sys.objects o 
        JOIN sys.tables t ON o.object_id = t.object_id
        """
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        # Should catch both sys.objects and sys.tables
        assert any(issue.code == "E_NOT_ALLOWLIST" for issue in result.issues)


class TestSystemObjectProtection:
    """Test protection against system object access."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"sys.objects"}  # Even if allowed, should be blocked
    
    def test_sys_objects_blocked(self):
        """Test that sys.objects access is blocked."""
        sql = "SELECT * FROM sys.objects"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_SYSTEM_OBJECT" for issue in result.issues)
    
    def test_information_schema_blocked(self):
        """Test that information_schema access is blocked."""
        sql = "SELECT * FROM information_schema.tables"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_SYSTEM_OBJECT" for issue in result.issues)
    
    def test_master_db_blocked(self):
        """Test that master database objects are blocked."""
        sql = "SELECT * FROM master.dbo.sysdatabases"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        # Should be blocked as both system object AND cross-database reference
        assert any(issue.code in ["E_SYSTEM_OBJECT", "E_CROSS_DB"] for issue in result.issues)


class TestCrossDatabaseReferences:
    """Test cross-database reference blocking."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"master.dbo.spt_values"}  # Even if allowed, should be blocked
    
    def test_three_part_name_blocked(self):
        """Test that database.schema.table names are blocked."""
        sql = "SELECT * FROM master.dbo.spt_values"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_CROSS_DB" for issue in result.issues)
        assert "master.dbo.spt_values" in str(result.issues)


class TestDeterministicResults:
    """Test deterministic result requirements."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"Production.Product"}
    
    def test_top_without_order_by_rejected(self):
        """Test that TOP without ORDER BY is rejected."""
        sql = "SELECT TOP 10 * FROM Production.Product"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_NO_ORDER_BY" for issue in result.issues)
        assert "TOP" in str(result.issues)
    
    def test_offset_fetch_without_order_by_rejected(self):
        """Test that OFFSET/FETCH without ORDER BY is rejected."""
        sql = """
        SELECT * FROM Production.Product 
        OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY
        """
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_NO_ORDER_BY" for issue in result.issues)
        assert "OFFSET" in str(result.issues)
    
    def test_top_with_order_by_accepted(self):
        """Test that TOP with ORDER BY is accepted."""
        sql = "SELECT TOP 10 * FROM Production.Product ORDER BY ProductID"
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0


class TestMultipleStatements:
    """Test multiple statement blocking."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"Production.Product"}
    
    def test_multiple_statements_rejected(self):
        """Test that multiple statements are rejected."""
        sql = "SELECT * FROM Production.Product; SELECT COUNT(*) FROM Production.Product;"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_MULTI_STMT" for issue in result.issues)
    
    def test_single_statement_with_semicolon_accepted(self):
        """Test that single statement with trailing semicolon is accepted."""
        sql = "SELECT * FROM Production.Product ORDER BY ProductID;"
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0


class TestDangerousPatterns:
    """Test dangerous pattern detection."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"Production.Product", "Sales.SalesOrderHeader"}
    
    def test_temp_table_rejected(self):
        """Test that temp tables are rejected."""
        sql = "SELECT * INTO #temp FROM Production.Product"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        assert any(issue.code == "E_TEMP_TABLE" for issue in result.issues)
    
    def test_dynamic_sql_rejected(self):
        """Test that dynamic SQL is rejected."""
        sql = "EXEC('SELECT * FROM Production.Product')"
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        # Should be caught by both banned operations AND dynamic SQL checks
        assert any(issue.code in ["E_NOT_SELECT", "E_DYNAMIC_SQL"] for issue in result.issues)
    
    def test_cross_join_warning(self):
        """Test that CROSS JOIN without WHERE generates warning."""
        sql = """
        SELECT * FROM Production.Product p 
        CROSS JOIN Sales.SalesOrderHeader s
        """
        result = validate_sql(sql, self.allowlist)
        # Should still be valid but have a warning
        assert any(issue.code == "W_CROSS_JOIN" for issue in result.issues)


class TestCommentHandling:
    """Test SQL comment handling and potential bypass attempts."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"Production.Product"}
    
    def test_single_line_comments_removed(self):
        """Test that single-line comments are properly removed."""
        sql = """
        SELECT ProductID -- This is a comment
        FROM Production.Product
        ORDER BY ProductID
        """
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0
    
    def test_multi_line_comments_removed(self):
        """Test that multi-line comments are properly removed."""
        sql = """
        SELECT ProductID /* This is a 
        multi-line comment */
        FROM Production.Product
        ORDER BY ProductID
        """
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0
    
    def test_comment_bypass_attempt_blocked(self):
        """Test that comment-based bypass attempts are blocked."""
        sql = """
        SELECT * FROM Production.Product; /* comment */ DELETE FROM Production.Product;
        """
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        # Should be blocked for multiple statements and/or DELETE operation
        assert any(issue.code in ["E_MULTI_STMT", "E_NOT_SELECT"] for issue in result.issues)


class TestWithCTEs:
    """Test WITH Common Table Expression support."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"Production.Product"}
    
    def test_with_cte_accepted(self):
        """Test that WITH CTEs are accepted."""
        sql = """
        WITH ProductCTE AS (
            SELECT ProductID, Name 
            FROM Production.Product 
            WHERE ProductID < 100
        )
        SELECT * FROM ProductCTE ORDER BY ProductID
        """
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0
        assert "Production.Product" in result.objects


class TestComplexScenarios:
    """Test complex real-world scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {
            "Sales.SalesOrderHeader",
            "Sales.SalesOrderDetail",
            "Production.Product",
            "Person.Person"
        }
    
    def test_complex_valid_query(self):
        """Test complex but valid query."""
        sql = """
        WITH OrderSummary AS (
            SELECT 
                soh.SalesOrderID,
                soh.CustomerID,
                soh.OrderDate,
                COUNT(sod.SalesOrderDetailID) AS ItemCount,
                SUM(sod.LineTotal) AS OrderTotal
            FROM Sales.SalesOrderHeader soh
            INNER JOIN Sales.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
            WHERE soh.OrderDate >= '2023-01-01'
            GROUP BY soh.SalesOrderID, soh.CustomerID, soh.OrderDate
        )
        SELECT TOP 100
            os.SalesOrderID,
            os.CustomerID,
            os.OrderDate,
            os.ItemCount,
            os.OrderTotal,
            p.Name as CustomerName
        FROM OrderSummary os
        LEFT JOIN Person.Person p ON os.CustomerID = p.BusinessEntityID
        ORDER BY os.OrderTotal DESC, os.SalesOrderID
        """
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert len(result.issues) == 0
        expected_objects = {
            "Sales.SalesOrderHeader", 
            "Sales.SalesOrderDetail", 
            "Person.Person"
        }
        assert expected_objects.issubset(result.objects)
    
    def test_complex_invalid_query(self):
        """Test complex query with multiple violations."""
        sql = """
        SELECT TOP 10 soh.SalesOrderID, COUNT(*) 
        FROM Sales.SalesOrderHeader soh
        LEFT JOIN UnauthorizedTable ut ON soh.CustomerID = ut.ID
        CROSS JOIN sys.tables st
        """
        result = validate_sql(sql, self.allowlist)
        assert not result.ok
        # Should have multiple issues: TOP without ORDER BY, unauthorized table, system object
        issue_codes = [issue.code for issue in result.issues]
        assert "E_NO_ORDER_BY" in issue_codes
        assert "E_NOT_ALLOWLIST" in issue_codes
        assert "E_SYSTEM_OBJECT" in issue_codes


class TestPerformanceAndEdgeCases:
    """Test performance requirements and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.allowlist = {"Production.Product"}
    
    def test_very_long_query(self):
        """Test handling of very long queries."""
        # Create a long but valid query
        columns = ", ".join([f"col{i}" for i in range(100)])
        sql = f"SELECT {columns} FROM Production.Product ORDER BY ProductID"
        
        result = validate_sql(sql, self.allowlist)
        # Should still validate successfully
        assert result.ok
        assert len(result.issues) == 0
    
    def test_deeply_nested_subqueries(self):
        """Test handling of deeply nested subqueries."""
        sql = """
        SELECT * FROM (
            SELECT * FROM (
                SELECT * FROM (
                    SELECT ProductID FROM Production.Product
                ) t1
            ) t2
        ) t3 
        ORDER BY ProductID
        """
        result = validate_sql(sql, self.allowlist)
        assert result.ok
        assert "Production.Product" in result.objects
    
    def test_malformed_sql(self):
        """Test handling of malformed SQL."""
        sql = "SELECT FROM WHERE ORDER BY"
        result = validate_sql(sql, self.allowlist)
        # Should handle gracefully with parse error
        assert not result.ok
        # Could be parse error or other validation issue
        assert len(result.issues) > 0
