import os
import pyodbc

# In a real application, these would be loaded from a secure config
# For the POC, we can use environment variables or hardcode them for simplicity
GPT_API_KEY = os.environ.get("GPT_API_KEY", "your_api_key_here")
DB_CONNECTION_STRING = os.environ.get(
    "DB_CONNECTION_STRING",
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks;UID=sa;PWD=yourStrong(!)Password"
)


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
    This function takes a natural language question and uses the GPT-5 API
    to convert it into a SQL query.

    For this POC, it returns a mock query.
    """
    # In a real implementation, you would make an API call to GPT-5 here.
    # Example:
    # headers = {"Authorization": f"Bearer {GPT_API_KEY}"}
    # response = await httpx.post("https://api.openai.com/v1/...", json={"prompt": question}, headers=headers)
    # sql_query = response.json()["choices"][0]["text"]

    print(f"Received question: {question}")
    mock_sql_query = f"SELECT TOP 10 * FROM Person.Person ORDER BY LastName;"
    print(f"Generated SQL: {mock_sql_query}")

    return mock_sql_query
