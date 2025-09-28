import os
import pyodbc
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
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
    You are a SQL expert working with the AdventureWorks2022 database. Here are the key tables and their relationships:
    
    PERSON TABLES:
    - Person.Person (BusinessEntityID, FirstName, LastName, EmailPromotion, etc.)
    - Person.EmailAddress (BusinessEntityID, EmailAddress)
    - Person.Address (AddressID, AddressLine1, City, StateProvinceID, PostalCode)
    
    PRODUCT TABLES:
    - Production.Product (ProductID, Name, ProductNumber, Color, Size, Weight, ListPrice, etc.)
    - Production.ProductCategory (ProductCategoryID, Name)
    - Production.ProductSubcategory (ProductSubcategoryID, Name, ProductCategoryID)
    
    SALES TABLES:
    - Sales.SalesOrderHeader (SalesOrderID, OrderDate, CustomerID, TotalDue, etc.)
    - Sales.SalesOrderDetail (SalesOrderID, ProductID, OrderQty, UnitPrice, LineTotal)
    - Sales.Customer (CustomerID, PersonID, StoreID)
    
    EMPLOYEE TABLES:
    - HumanResources.Employee (BusinessEntityID, JobTitle, HireDate, etc.)
    - HumanResources.Department (DepartmentID, Name)
    
    Always use proper SQL Server syntax with TOP instead of LIMIT, and include appropriate JOINs when needed.
    Return ONLY the SQL query, no explanations or markdown formatting.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": schema_context
                },
                {
                    "role": "user", 
                    "content": f"Convert this question to a SQL query: {question}"
                }
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        sql_query = response.choices[0].message.content
        if sql_query is None:
            sql_query = "SELECT TOP 10 FirstName, LastName FROM Person.Person ORDER BY LastName;"
        else:
            sql_query = sql_query.strip()
            # Clean up the response - remove any markdown formatting
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        print(f"Generated SQL: {sql_query}")
        return sql_query
        
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        # Fallback to a simple query
        fallback_query = "SELECT TOP 10 FirstName, LastName FROM Person.Person ORDER BY LastName;"
        print(f"Using fallback SQL: {fallback_query}")
        return fallback_query
