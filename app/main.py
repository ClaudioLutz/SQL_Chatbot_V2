from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import pandas as pd

from . import services
from . import analysis_service
from . import visualization_service

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
        
    Returns:
        Prepared data with sampling info and column types
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.rows)
        
        # Check row limit (consistent with analysis feature)
        if len(df) > 50000:
            return {
                "status": "too_large",
                "row_count": len(df),
                "message": "Dataset exceeds 50,000 rows. Please refine your query."
            }
        
        # Prepare visualization data (with sampling if needed)
        result = visualization_service.prepare_visualization_data(
            df=df,
            chart_type=request.chartType,
            x_column=request.xColumn,
            y_column=request.yColumn,
            max_rows=10000
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
