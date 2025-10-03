#!/usr/bin/env python3
"""
Test script to verify SQL Server connection using Windows Authentication
Server: PRODSVCREPORT70
Database: CnZenReport
Driver: ODBC Driver 17 for SQL Server
"""
import pyodbc

# Connection parameters
DEFAULT_DRIVER = 'ODBC Driver 17 for SQL Server'
DEFAULT_SERVER = 'PRODSVCREPORT70'
DEFAULT_DB = 'CnZenReport'

# Windows Authentication connection string
# Trusted_Connection=Yes uses your current Windows credentials
DB_CONNECTION_STRING = f"DRIVER={{{DEFAULT_DRIVER}}};SERVER={DEFAULT_SERVER};DATABASE={DEFAULT_DB};Trusted_Connection=Yes;"

def test_connection():
    """Test database connection and basic query"""
    try:
        print("=" * 70)
        print("Testing SQL Server Connection with Windows Authentication")
        print("=" * 70)
        print(f"Driver: {DEFAULT_DRIVER}")
        print(f"Server: {DEFAULT_SERVER}")
        print(f"Database: {DEFAULT_DB}")
        print(f"Authentication: Windows (Trusted Connection)")
        print("=" * 70)
        
        print("\n1. Attempting to connect...")
        with pyodbc.connect(DB_CONNECTION_STRING, timeout=10) as cnxn:
            cursor = cnxn.cursor()
            
            # Test 1: Get SQL Server version
            print("\n2. Testing basic connection - Getting SQL Server version...")
            cursor.execute("SELECT @@VERSION AS ServerVersion")
            version = cursor.fetchone()[0]
            print(f"✓ Connected successfully!")
            print(f"  SQL Server Version: {version[:100]}...")
            
            # Test 2: Get current database
            print("\n3. Verifying database context...")
            cursor.execute("SELECT DB_NAME() AS CurrentDatabase")
            current_db = cursor.fetchone()[0]
            print(f"✓ Current Database: {current_db}")
            
            # Test 3: Get current user
            print("\n4. Checking authentication...")
            cursor.execute("SELECT SYSTEM_USER AS CurrentUser, SUSER_NAME() AS LoginName")
            row = cursor.fetchone()
            print(f"✓ Connected as: {row[0]}")
            print(f"  Login Name: {row[1]}")
            
            # Test 4: List first few tables in database
            print("\n5. Listing available tables (first 10)...")
            cursor.execute("""
                SELECT TOP 10 
                    TABLE_SCHEMA + '.' + TABLE_NAME AS TableName,
                    TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES 
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            tables = cursor.fetchall()
            if tables:
                print(f"✓ Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table[0]} ({table[1]})")
            else:
                print("  No tables found or insufficient permissions")
            
            print("\n" + "=" * 70)
            print("✓ CONNECTION TEST SUCCESSFUL!")
            print("=" * 70)
            return True
            
    except pyodbc.Error as e:
        print("\n" + "=" * 70)
        print("✗ CONNECTION FAILED")
        print("=" * 70)
        
        # Provide detailed error information
        sqlstate = e.args[0] if len(e.args) > 0 else "Unknown"
        message = e.args[1] if len(e.args) > 1 else str(e)
        
        print(f"Error Code: {sqlstate}")
        print(f"Error Message: {message}")
        
        # Common troubleshooting tips
        print("\nTroubleshooting Tips:")
        print("1. Verify you have network access to server: PRODSVCREPORT70")
        print("2. Check if SQL Server Browser service is running on the server")
        print("3. Verify Windows Authentication is enabled on SQL Server")
        print("4. Confirm you have access rights to the CnZenReport database")
        print("5. Check if 'ODBC Driver 17 for SQL Server' is installed")
        print("   - Run: odbcinst -q -d  (PowerShell/CMD)")
        print("6. Try adding port explicitly: SERVER=PRODSVCREPORT70,1433")
        print("7. If firewall blocks connection, contact your network admin")
        
        return False
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("✗ UNEXPECTED ERROR")
        print("=" * 70)
        print(f"Error: {type(e).__name__}: {e}")
        return False

def test_alternative_connection_strings():
    """Test alternative connection string formats if main one fails"""
    print("\n\nTrying alternative connection string formats...\n")
    
    alternatives = [
        # With explicit port
        f"DRIVER={{{DEFAULT_DRIVER}}};SERVER={DEFAULT_SERVER},1433;DATABASE={DEFAULT_DB};Trusted_Connection=Yes;",
        # With timeout
        f"DRIVER={{{DEFAULT_DRIVER}}};SERVER={DEFAULT_SERVER};DATABASE={DEFAULT_DB};Trusted_Connection=Yes;Connection Timeout=30;",
        # With encryption settings
        f"DRIVER={{{DEFAULT_DRIVER}}};SERVER={DEFAULT_SERVER};DATABASE={DEFAULT_DB};Trusted_Connection=Yes;Encrypt=No;",
        # With encryption and trust settings
        f"DRIVER={{{DEFAULT_DRIVER}}};SERVER={DEFAULT_SERVER};DATABASE={DEFAULT_DB};Trusted_Connection=Yes;Encrypt=Yes;TrustServerCertificate=Yes;",
    ]
    
    for i, conn_str in enumerate(alternatives, 1):
        print(f"\nAlternative {i}:")
        print(f"Connection String: {conn_str}")
        try:
            with pyodbc.connect(conn_str, timeout=10) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute("SELECT @@VERSION")
                cursor.fetchone()
                print("✓ This connection string works!")
                print(f"\nUse this in your .env file:")
                print(f"DB_CONNECTION_STRING={conn_str}")
                return conn_str
        except Exception as e:
            print(f"✗ Failed: {str(e)[:100]}")
    
    return None

if __name__ == "__main__":
    success = test_connection()
    
    if not success:
        print("\n" + "=" * 70)
        print("Main connection failed. Testing alternatives...")
        print("=" * 70)
        working_string = test_alternative_connection_strings()
        
        if working_string:
            print("\n✓ Found a working connection string!")
        else:
            print("\n✗ All connection attempts failed.")
            print("Please check the troubleshooting tips above.")
