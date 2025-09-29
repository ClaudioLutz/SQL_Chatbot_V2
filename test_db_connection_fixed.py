#!/usr/bin/env python3
"""
Test script that uses the same configuration as the main application
"""
import os
from dotenv import load_dotenv
import pyodbc

# Load environment variables
load_dotenv()

# Get connection string from environment (same as services.py)
DB_CONNECTION_STRING = os.environ.get(
    "DB_CONNECTION_STRING",
    "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2022;UID=sa;PWD=YourStrong!Passw0rd;Encrypt=Yes;TrustServerCertificate=Yes"
)

def test_connection():
    """Test database connection and sample query"""
    try:
        print("Testing database connection...")
        print(f"Using connection string: {DB_CONNECTION_STRING.replace(';PWD=StrongP@ss!;', ';PWD=***;')}")
        
        with pyodbc.connect(DB_CONNECTION_STRING) as cnxn:
            cursor = cnxn.cursor()
            
            # Test basic connection
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"✓ Connected to SQL Server: {version[:50]}...")
            
            # Test database exists
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            print(f"✓ Connected to database: {db_name}")
            
            # Test AdventureWorks data
            cursor.execute("SELECT TOP 3 Name FROM Production.Product ORDER BY ProductID;")
            products = [row[0] for row in cursor.fetchall()]
            print(f"✓ Sample products from AdventureWorks: {products}")
            
            # Test Person table (used in queries)
            cursor.execute("SELECT TOP 3 FirstName, LastName FROM Person.Person ORDER BY LastName;")
            people = [(row[0], row[1]) for row in cursor.fetchall()]
            print(f"✓ Sample people from Person table: {people}")
            
            print("✓ Database connection test successful!")
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if not success:
        print("\n" + "="*60)
        print("DATABASE SETUP HELP:")
        print("="*60)
        print("1. Make sure SQL Server is running on localhost:1433")
        print("2. Restore the AdventureWorks2022.bak file if not done yet")
        print("3. Create the 'chatbot_ro' user with read-only permissions")
        print("4. Or update the .env file with correct credentials")
