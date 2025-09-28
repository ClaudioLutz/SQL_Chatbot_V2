import os
import pyodbc
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")  # set to your provisioned GPT-5 model
DB_CONNECTION_STRING = os.environ.get(
    "DB_CONNECTION_STRING",
    "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2022;UID=sa;PWD=YourStrong!Passw0rd;Encrypt=Yes;TrustServerCertificate=Yes"
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def execute_sql_query(sql_query: str) -> dict:
    """
    Executes a SQL query against the database and returns the results.
    """
    results = []
    columns = []
    try:
        with pyodbc.connect(DB_CONNECTION_STRING) as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(sql_query)
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
    except Exception as e:
        print(f"Database query failed: {e}")
        return {"error": str(e)}

    return {"columns": columns, "rows": results}


async def get_sql_from_gpt(question: str) -> str:
    """
    This function takes a natural language question and uses the OpenAI API
    to convert it into a SQL query for the AdventureWorks database.
    """
    print(f"Received question: {question}")
    
    # AdventureWorks database schema context
    schema_context = """
    You are a SQL expert for the AdventureWorks2022 SQL Server database.
    Rules:
      - Return **only** a single SQL SELECT statement. No markdown, no comments, no prose.
      - Use SQL Server syntax (TOP n, CONVERT/CAST, GETDATE(), etc.). Never use LIMIT.
      - If the user asks "how many ...", use COUNT(*) and alias the column clearly (e.g., AS EmployeeCount).
      - Employees live in HumanResources.Employee. Names/emails live in Person.* tables.
      - Prefer exact joins on keys (e.g., BusinessEntityID) and fully-qualify schema names (Person.Person).
      - Reject non-SELECT operations (INSERT/UPDATE/DELETE/DDL).

    Key tables (not exhaustive):
    PERSON TABLES:
      - Person.Person (BusinessEntityID, FirstName, LastName, EmailPromotion, etc.)
      - Person.EmailAddress (BusinessEntityID, EmailAddress)
      - Person.Address (AddressID, AddressLine1, City, StateProvinceID, PostalCode)
    PRODUCT TABLES:
      - Production.Product (...), Production.ProductCategory, Production.ProductSubcategory
    SALES TABLES:
      - Sales.SalesOrderHeader, Sales.SalesOrderDetail, Sales.Customer
    EMPLOYEE TABLES:
      - HumanResources.Employee (BusinessEntityID, JobTitle, HireDate, etc.)
      - HumanResources.Department (DepartmentID, Name)
    """
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": schema_context},
                {"role": "user", "content": 
                  f"Convert the user question to ONE valid SQL Server SELECT statement. "
                  f"Do not include markdown. Question: {question}"}
            ],
            max_completion_tokens=200
        )
        
        sql_query = (response.choices[0].message.content or "").strip()
        if sql_query is None:
            sql_query = "SELECT TOP 10 FirstName, LastName FROM Person.Person ORDER BY LastName;"
        else:
            sql_query = sql_query.strip()
            # Remove code fences / markdown if any:
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            # Enforce SELECT-only:
            if not sql_query.lower().startswith("select"):
                raise ValueError("LLM returned a non-SELECT statement")
        
        print(f"Generated SQL: {sql_query}")
        return sql_query
        
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        # Fallback to a simple query
        fallback_query = "SELECT TOP 10 FirstName, LastName FROM Person.Person ORDER BY LastName;"
        print(f"Using fallback SQL: {fallback_query}")
        return fallback_query
