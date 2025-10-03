import requests
import json

# Test the execute-sql endpoint
sql = """
SELECT TOP (5) [CrefoId]
      ,[OneCrefoId]
      ,[ArchivNr]
      ,[Name]
      ,[Name2]
      ,[Vorname]
      ,[Strasse]
      ,[Hausnummer]
  FROM [CnZenReport].[prod_reporting].[Archiv]
"""

print("=== Testing API Endpoint ===\n")

response = requests.post(
    'http://localhost:8000/api/execute-sql',
    json={'sql': sql},
    headers={'Content-Type': 'application/json'}
)

print(f"Status Code: {response.status_code}\n")

data = response.json()

print(f"Columns: {data['results']['columns']}\n")

if data['results']['rows']:
    print(f"First row:")
    first_row = data['results']['rows'][0]
    for key, value in first_row.items():
        print(f"  {key}: {repr(value)}")
    
    print(f"\n=== JSON Response (first row) ===")
    print(json.dumps(first_row, indent=2, default=str))
