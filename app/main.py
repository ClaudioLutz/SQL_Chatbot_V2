from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import services

app = FastAPI()


class QueryRequest(BaseModel):
    question: str


@app.post("/api/query")
async def run_query(request: QueryRequest):
    sql_query = await services.get_sql_from_gpt(request.question)
    results = services.execute_sql_query(sql_query)
    return {"sql_query": sql_query, "results": results}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
