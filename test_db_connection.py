#!/usr/bin/env python3
"""
Quick test script to verify AdventureWorks2022 database connectivity
"""
import pyodbc

# Connection string from services.py
DB_CONNECTION_STRING = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2022;UID=sa;PWD=YourStrong!Passw0rd;Encrypt=Yes;TrustServerCertificate=Yes"

def test_connection():
    """Test database connection and sample query"""
    try:
        print("Testing database connection...")
        with pyodbc.connect(DB_CONNECTION_STRING) as cnxn:
            cursor = cnxn.cursor()
            
            # Test basic connection
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"✓ Connected to SQL Server: {version[:50]}...")
            
            # Test AdventureWorks data
            cursor.execute("SELECT TOP 3 Name FROM Production.Product ORDER BY ProductID;")
            products = [row[0] for row in cursor.fetchall()]
            print(f"✓ Sample products from AdventureWorks: {products}")
            
            # Test Person table (used in mock query)
            cursor.execute("SELECT TOP 3 FirstName, LastName FROM Person.Person ORDER BY LastName;")
            people = [(row[0], row[1]) for row in cursor.fetchall()]
            print(f"✓ Sample people from Person table: {people}")
            
            print("✓ Database connection test successful!")
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
