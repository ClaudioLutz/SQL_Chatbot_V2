#!/usr/bin/env python3
"""
Test to verify that the original failing CTE query from the error report would now be accepted.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services import _is_safe_select

def test_original_failing_query():
    """Test the exact CTE query that was failing before."""
    
    print("Testing the original failing CTE query...\n")
    
    # The exact query that was being rejected before the fix
    original_query = """WITH MostExpensiveProduct AS (
    SELECT TOP 1 p.ProductID, p.Name AS ProductName, p.ProductNumber, p.ListPrice
    FROM Production.Product p
    ORDER BY p.ListPrice DESC, p.ProductID
),
SalesBySalesperson AS (
    SELECT soh.SalesPersonID, SUM(sod.LineTotal) AS TotalRevenue
    FROM Sales.SalesOrderDetail sod
    INNER JOIN Sales.SalesOrderHeader soh ON sod.SalesOrderID = soh.SalesOrderID
    INNER JOIN MostExpensiveProduct mep ON mep.ProductID = sod.ProductID
    WHERE soh.SalesPersonID IS NOT NULL
    GROUP BY soh.SalesPersonID
)
SELECT TOP 1
    mep.ProductID,
    mep.ProductName,
    mep.ProductNumber,
    mep.ListPrice,
    sp.BusinessEntityID AS SalesPersonID,
    pp.FirstName AS SalesPersonFirstName,
    pp.LastName AS SalesPersonLastName,
    sbs.TotalRevenue AS TotalRevenueForProduct
FROM SalesBySalesperson sbs
INNER JOIN Sales.SalesPerson sp ON sp.BusinessEntityID = sbs.SalesPersonID
INNER JOIN Person.Person pp ON pp.BusinessEntityID = sp.BusinessEntityID
CROSS JOIN MostExpensiveProduct mep
ORDER BY sbs.TotalRevenue DESC, sp.BusinessEntityID"""
    
    print(f"Original query (first 100 chars): {original_query[:100]}...")
    print(f"Full query length: {len(original_query)} characters")
    print()
    
    # Test the validation
    try:
        result = _is_safe_select(original_query)
        if result:
            print("✅ SUCCESS: The original failing CTE query is now ACCEPTED!")
            print("🎉 The fix works! CTEs starting with WITH are now properly supported.")
            return True
        else:
            print("❌ FAILURE: The query is still being rejected.")
            print("⚠️  The fix may not be working properly.")
            return False
            
    except Exception as e:
        print(f"💥 ERROR: Exception occurred during validation: {e}")
        return False

if __name__ == "__main__":
    success = test_original_failing_query()
    print("\n" + "="*60)
    if success:
        print("RESULT: Fix is working correctly! 🎉")
        print("CTEs (Common Table Expressions) are now supported.")
    else:
        print("RESULT: Fix needs further investigation. ⚠️")
    print("="*60)
    
    sys.exit(0 if success else 1)
