import pyodbc
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")

sql = """
SELECT TOP (5) [CrefoId]
      ,[OneCrefoId]
      ,[ArchivNr]
      ,[Name]
      ,[Name2]
      ,[Vorname]
      ,[Strasse]
      ,[Hausnummer]
      ,[Plz]
      ,[Ort]
      ,[LandCode]
      ,[Zusatz]
      ,[Postfach]
      ,[Telefon]
      ,[Fax]
      ,[Email]
  FROM [CnZenReport].[prod_reporting].[Archiv]
"""

print("=== Testing Database Query ===\n")

with pyodbc.connect(DB_CONNECTION_STRING) as cnxn:
    cursor = cnxn.cursor()
    cursor.execute(sql)
    
    # Get column names
    columns = [column[0] for column in cursor.description]
    print(f"Column names ({len(columns)} total):")
    for i, col in enumerate(columns):
        print(f"  {i}: '{col}' (type: {type(col).__name__})")
    
    print("\n" + "="*50 + "\n")
    
    # Get first row
    row = cursor.fetchone()
    
    print(f"First row data ({len(row)} values):")
    for i, val in enumerate(row):
        print(f"  {i}: {repr(val)} (type: {type(val).__name__})")
    
    print("\n" + "="*50 + "\n")
    
    # Create dictionary using zip (old method)
    row_dict_zip = dict(zip(columns, row))
    print("Dictionary created with zip():")
    for key, val in row_dict_zip.items():
        print(f"  '{key}': {repr(val)}")
    
    print("\n" + "="*50 + "\n")
    
    # Create dictionary using index (new method)
    row_dict_index = {}
    for i, col_name in enumerate(columns):
        row_dict_index[col_name] = row[i]
    
    print("Dictionary created with index:")
    for key, val in row_dict_index.items():
        print(f"  '{key}': {repr(val)}")
    
    print("\n" + "="*50 + "\n")
    
    # Compare
    print("Comparison:")
    print(f"  zip() result == index() result: {row_dict_zip == row_dict_index}")
    
    # Check JSON serialization
    print("\nJSON serialization test:")
    try:
        json_zip = json.dumps({"columns": columns, "rows": [row_dict_zip]}, default=str)
        print(f"  zip() JSON: {json_zip[:200]}...")
    except Exception as e:
        print(f"  zip() JSON ERROR: {e}")
    
    try:
        json_index = json.dumps({"columns": columns, "rows": [row_dict_index]}, default=str)
        print(f"  index() JSON: {json_index[:200]}...")
    except Exception as e:
        print(f"  index() JSON ERROR: {e}")
