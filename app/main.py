from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging

from . import services
from . import analysis_service

logger = logging.getLogger(__name__)

app = FastAPI()


class QueryRequest(BaseModel):
    question: str


class AnalyzeRequest(BaseModel):
    columns: list[str]
    rows: list[dict]


@app.post("/api/query")
async def run_query(request: QueryRequest):
    sql_query = await services.get_sql_from_gpt(request.question)
    results = services.execute_sql_query(sql_query)
    return {"sql_query": sql_query, "results": results}


@app.post("/api/analyze")
async def analyze_results(request: AnalyzeRequest):
    """
    Generate statistical analysis for query results.
    
    Request body:
        columns: List of column names
        rows: List of row dictionaries
        
    Returns:
        Analysis data with status: success/too_large/error
    """
    try:
        analysis = analysis_service.analyze_query_results(
            columns=request.columns,
            rows=request.rows
        )
        return analysis
    except Exception as e:
        logger.error(f"Analysis endpoint error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Analysis could not be generated for this dataset.",
            "error_detail": str(e)
        }


app.mount("/", StaticFiles(directory="static", html=True), name="static")
