#!/usr/bin/env python3
"""
Test script to verify that the CTE fix works properly.
Tests both regular SELECT statements and WITH (CTE) statements.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services import _is_safe_select

def test_cte_validation():
    """Test that the _is_safe_select function works correctly with CTEs."""
    
    print("Testing SQL validation with CTE support...\n")
    
    # Test cases: (sql, expected_result, description)
    test_cases = [
        # Regular SELECT statements (should pass)
        ("SELECT * FROM Person.Person", True, "Basic SELECT statement"),
        ("select name from Production.Product", True, "Lowercase SELECT statement"),
        
        # CTE statements (should now pass)
        ("WITH MostExpensive AS (SELECT TOP 1 * FROM Production.Product ORDER BY ListPrice DESC) SELECT * FROM MostExpensive", 
         True, "CTE with WITH clause"),
        ("with cte as (select count(*) as cnt from Person.Person) select * from cte", 
         True, "Lowercase WITH clause"),
        
        # Multiple CTEs (should pass)
        ("WITH CTE1 AS (SELECT * FROM Person.Person), CTE2 AS (SELECT * FROM Production.Product) SELECT * FROM CTE1", 
         True, "Multiple CTEs"),
        
        # Dangerous SQL (should still fail)
        ("DROP TABLE Person.Person", False, "DROP statement (dangerous)"),
        ("DELETE FROM Person.Person", False, "DELETE statement (dangerous)"),
        ("UPDATE Person.Person SET FirstName = 'Test'", False, "UPDATE statement (dangerous)"),
        ("INSERT INTO Person.Person VALUES (1, 'Test', 'User')", False, "INSERT statement (dangerous)"),
        
        # Invalid starting keywords (should fail)
        ("CREATE TABLE test (id int)", False, "CREATE statement"),
        ("EXEC sp_helpdb", False, "EXEC statement"),
        
        # Multiple statements (should fail)
        ("SELECT * FROM Person.Person; DROP TABLE Person.Person", False, "Multiple statements with semicolon"),
        
        # Edge cases
        ("", False, "Empty string"),
        ("   ", False, "Whitespace only"),
        ("SOMETHING ELSE", False, "Invalid starting keyword"),
    ]
    
    passed = 0
    failed = 0
    
    for sql, expected, description in test_cases:
        try:
            result = _is_safe_select(sql)
            if result == expected:
                print(f"✅ PASS: {description}")
                print(f"   SQL: {sql[:60]}{'...' if len(sql) > 60 else ''}")
                print(f"   Expected: {expected}, Got: {result}\n")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   SQL: {sql[:60]}{'...' if len(sql) > 60 else ''}")
                print(f"   Expected: {expected}, Got: {result}\n")
                failed += 1
        except Exception as e:
            print(f"💥 ERROR: {description}")
            print(f"   SQL: {sql[:60]}{'...' if len(sql) > 60 else ''}")
            print(f"   Exception: {e}\n")
            failed += 1
    
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! CTE support is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = test_cte_validation()
    sys.exit(0 if success else 1)
