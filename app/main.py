from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import logging
import pandas as pd
import time

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from . import services
from . import analysis_service
from . import visualization_service

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class QueryRequest(BaseModel):
    question: str


class ExecuteSQLRequest(BaseModel):
    sql: str


class QueryResponse(BaseModel):
    sql_query: str
    question: Optional[str] = None
    results: dict
    execution_time_ms: Optional[float] = None
    row_count: int
    error: Optional[str] = None
    error_code: Optional[str] = None


class AnalyzeRequest(BaseModel):
    columns: list[str]
    rows: list[dict]


@app.post("/api/query")
async def run_query(request: QueryRequest):
    sql_query = await services.get_sql_from_gpt(request.question)
    results = services.execute_sql_query(sql_query)
    return {"sql_query": sql_query, "results": results}


@app.post("/api/execute-sql")
@limiter.limit("30/minute")
async def execute_sql(request: Request, sql_request: ExecuteSQLRequest):
    """
    Execute a user-provided SQL query with validation and rate limiting.
    
    This endpoint allows manual SQL execution while maintaining security through:
    - SQL validation (SELECT-only queries)
    - Rate limiting (30 requests per minute)
    - Sanitized logging
    - 30-second query timeout
    
    Request body:
        sql: SQL SELECT statement to execute
        
    Returns:
        QueryResponse with results or error information
    """
    sql = sql_request.sql.strip()
    client_ip = request.client.host if request.client else "unknown"
    
    # Log request with sanitized SQL
    logger.info(
        f"MANUAL_SQL_START | IP: {client_ip} | "
        f"HASH: {services.get_sql_hash(sql)} | "
        f"SQL: {services.sanitize_sql_for_logging(sql)}"
    )
    
    # Validate SQL safety
    if not services.is_safe_select(sql):
        logger.warning(
            f"MANUAL_SQL_REJECTED | IP: {client_ip} | "
            f"HASH: {services.get_sql_hash(sql)} | "
            f"REASON: Validation failed"
        )
        return {
            "sql_query": sql,
            "question": None,
            "results": {"columns": [], "rows": []},
            "row_count": 0,
            "error": "Only SELECT statements are allowed. No data modification operations permitted.",
            "error_code": "VALIDATION_FAILED"
        }
    
    # Execute query
    start_time = time.time()
    try:
        results = services.execute_sql_query(sql)
        execution_time_ms = (time.time() - start_time) * 1000
        
        if "error" in results:
            # Database error
            logger.error(
                f"MANUAL_SQL_ERROR | IP: {client_ip} | "
                f"HASH: {services.get_sql_hash(sql)} | "
                f"ERROR: {results['error']}"
            )
            return {
                "sql_query": sql,
                "question": None,
                "results": {"columns": [], "rows": []},
                "row_count": 0,
                "execution_time_ms": execution_time_ms,
                "error": results["error"],
                "error_code": "DB_ERROR"
            }
        
        # Success
        row_count = len(results.get("rows", []))
        logger.info(
            f"MANUAL_SQL_SUCCESS | IP: {client_ip} | "
            f"HASH: {services.get_sql_hash(sql)} | "
            f"ROWS: {row_count} | TIME: {execution_time_ms:.2f}ms"
        )
        
        return {
            "sql_query": sql,
            "question": None,
            "results": results,
            "row_count": row_count,
            "execution_time_ms": execution_time_ms
        }
        
    except Exception as e:
        execution_time_ms = (time.time() - start_time) * 1000
        logger.error(
            f"MANUAL_SQL_EXCEPTION | IP: {client_ip} | "
            f"HASH: {services.get_sql_hash(sql)} | "
            f"ERROR: {str(e)}",
            exc_info=True
        )
        return {
            "sql_query": sql,
            "question": None,
            "results": {"columns": [], "rows": []},
            "row_count": 0,
            "execution_time_ms": execution_time_ms,
            "error": "An internal error occurred while executing the query.",
            "error_code": "INTERNAL_ERROR"
        }


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


@app.post("/api/check-visualization")
async def check_visualization(request: AnalyzeRequest):
    """
    Check if query results are suitable for visualization.
    
    Request body:
        columns: List of column names
        rows: List of row dictionaries
        
    Returns:
        Availability status with column types if available
    """
    try:
        availability = visualization_service.check_visualization_availability(
            columns=request.columns,
            rows=request.rows
        )
        return availability
    except Exception as e:
        logger.error(f"Visualization check error: {str(e)}", exc_info=True)
        return {
            "available": False,
            "reason": "Error checking visualization availability."
        }


@app.post("/api/visualize")
async def visualize_data(request: visualization_service.VisualizationRequest):
    """
    Prepare visualization data with sampling for large datasets.
    
    Request body:
        columns: List of column names
        rows: List of row dictionaries
        chartType: Type of chart (scatter, bar, line, histogram)
        xColumn: Name of X-axis column
        yColumn: Name of Y-axis column (optional for histogram)
        maxRows: Maximum rows to sample (optional, defaults to 10000)
        
    Returns:
        Prepared data with sampling info and column types
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.rows)
        
        # Get max_rows from request (Pydantic model field)
        max_rows = request.maxRows if request.maxRows is not None else 10000
        
        # Debug logging
        logger.info(f"Visualization request: maxRows={request.maxRows}, using max_rows={max_rows}, dataset_size={len(df)}")
        
        # Prepare visualization data (with sampling if needed)
        # Note: Large datasets will be automatically sampled to max_rows for performance
        result = visualization_service.prepare_visualization_data(
            df=df,
            chart_type=request.chartType,
            x_column=request.xColumn,
            y_column=request.yColumn,
            max_rows=max_rows
        )
        
        return result
        
    except ValueError as e:
        # Validation errors (incompatible column types)
        logger.warning(f"Visualization validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "error_type": "validation"
        }
    except Exception as e:
        # Unexpected errors
        logger.error(f"Visualization error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Failed to generate visualization data. Please try again.",
            "error_type": "server"
        }


app.mount("/", StaticFiles(directory="static", html=True), name="static")
