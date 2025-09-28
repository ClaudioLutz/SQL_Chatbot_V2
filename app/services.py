import os
import pyodbc
import traceback
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4")
DB_CONNECTION_STRING = os.environ.get(
    "DB_CONNECTION_STRING",
    "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2022;UID=sa;PWD=YourStrong!Passw0rd;Encrypt=Yes;TrustServerCertificate=Yes"
)

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def _is_safe_select(sql: str) -> bool:
    """Validate that SQL is a safe SELECT statement only."""
    s = sql.strip().lower()
    if not s.startswith("select"):
        return False
    
    # Check for dangerous keywords
    dangerous_keywords = [
        "drop ", "delete ", "update ", "insert ", "alter ", "create ",
        "truncate ", "exec ", "execute ", "sp_", "xp_", "--", "/*", "*/"
    ]
    
    for keyword in dangerous_keywords:
        if keyword in s:
            return False
    
    # Check for multiple statements (semicolons not at the end)
    sql_clean = s.rstrip(";")
    if ";" in sql_clean:
        return False
        
    return True


def _add_row_limit_if_needed(sql_query: str) -> str:
    """Add TOP 200 limit if query doesn't have aggregation or existing TOP clause."""
    sql_lower = sql_query.lower()
    
    # Skip if already has TOP clause or contains aggregation functions
    has_top = " top " in sql_lower or "top(" in sql_lower
    has_aggregation = any(func in sql_lower for func in ["count(", "avg(", "sum(", "max(", "min(", "group by"])
    
    if not has_top and not has_aggregation:
        # Add TOP 200 after SELECT
        return sql_query.replace("SELECT", "SELECT TOP 200", 1).replace("select", "SELECT TOP 200", 1)
    
    return sql_query


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
    
    # Enhanced AdventureWorks database schema context
    schema_context = """
    You are a SQL expert for the AdventureWorks2022 SQL Server database.
    
    CRITICAL RULES:
    - Return **only** a single SQL SELECT statement. No markdown, no comments, no prose.
    - Use SQL Server syntax (TOP n, CONVERT/CAST, GETDATE(), DATEDIFF, etc.). Never use LIMIT.
    - You must return a single SELECT statement compatible with SQL Server.
    - Use TOP instead of LIMIT. Never modify data.
    - For "how many ...", use COUNT(*) and alias clearly (e.g., AS EmployeeCount).
    - For age calculations, use AVG(DATEDIFF(year, BirthDate, GETDATE())) AS AvgAge.
    - Treat "employees" as HumanResources.Employee table.
    - Cap results with TOP 200 unless the user asks for an aggregate.
    - Always fully-qualify schema names (Person.Person, HumanResources.Employee, etc.).

    COMMON BUSINESS QUESTIONS MAPPING:
    - "how many employees" → COUNT(*) FROM HumanResources.Employee WHERE CurrentFlag = 1
    - "average age of employees" → AVG(DATEDIFF(year, BirthDate, GETDATE())) FROM HumanResources.Employee e JOIN Person.Person p ON e.BusinessEntityID = p.BusinessEntityID
    - "top products by sales" → use Sales.SalesOrderDetail and Production.Product tables with SUM(LineTotal)
    - "employee information" → join HumanResources.Employee with Person.Person on BusinessEntityID

    KEY TABLES & COLUMNS:
    PERSON TABLES:
    - Person.Person (BusinessEntityID, FirstName, LastName, PersonType, ModifiedDate)
    - Person.EmailAddress (BusinessEntityID, EmailAddress)
    - Person.Address (AddressID, AddressLine1, City, StateProvinceID, PostalCode)

    EMPLOYEE TABLES:
    - HumanResources.Employee (BusinessEntityID, NationalIDNumber, LoginID, JobTitle, BirthDate, MaritalStatus, Gender, HireDate, CurrentFlag, etc.)
    - HumanResources.Department (DepartmentID, Name, GroupName)
    - HumanResources.EmployeeDepartmentHistory (BusinessEntityID, DepartmentID, ShiftID, StartDate, EndDate)

    PRODUCT TABLES:
    - Production.Product (ProductID, Name, ProductNumber, Color, StandardCost, ListPrice, etc.)
    - Production.ProductCategory (ProductCategoryID, Name)
    - Production.ProductSubcategory (ProductSubcategoryID, ProductCategoryID, Name)

    SALES TABLES:
    - Sales.SalesOrderHeader (SalesOrderID, CustomerID, OrderDate, TotalDue, etc.)
    - Sales.SalesOrderDetail (SalesOrderDetailID, SalesOrderID, ProductID, OrderQty, UnitPrice, LineTotal)
    - Sales.Customer (CustomerID, PersonID, StoreID, AccountNumber)
    """
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": schema_context},
                {"role": "user", "content": f"Question: {question}"}
            ],
            max_completion_tokens=300,
            temperature=0.1
        )
        
        sql_query = (response.choices[0].message.content or "").strip()
        
        if not sql_query:
            raise ValueError("Empty response from OpenAI API")
        
        # Clean up the response
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Validate the SQL is safe
        if not _is_safe_select(sql_query):
            raise ValueError(f"Unsafe or non-SELECT SQL generated: {sql_query}")
        
        # Add row limit if needed
        sql_query = _add_row_limit_if_needed(sql_query)
        
        print(f"Generated SQL: {sql_query}")
        return sql_query
        
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        
        # Fallback to a simple query
        fallback_query = "SELECT TOP 10 FirstName, LastName FROM Person.Person ORDER BY LastName;"
        print(f"Using fallback SQL: {fallback_query}")
        return fallback_query
