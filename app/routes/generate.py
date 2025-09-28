"""
API route for SQL generation and execution.

This module provides the /api/generate endpoint that:
- Accepts natural language queries
- Generates T-SQL using LLM
- Validates SQL through safety layer
- Executes queries against the database
- Returns paginated results with metadata
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field, validator

from app.llm.sql_generator import sql_generator, SqlGenResult
from app.db.exec import db_executor, QueryResult, ExecutionError
from app.config import settings


logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request model for SQL generation endpoint."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    page: int = Field(default=1, ge=1, le=1000, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of results per page")

    @validator('prompt')
    def prompt_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty or only whitespace')
        return v.strip()


class GenerateSuccessResponse(BaseModel):
    """Success response model for SQL generation."""
    sql: str
    columns: list[Dict[str, str]]
    rows: list[list[Any]]
    page: int
    page_size: int
    meta: Dict[str, Any]


class GenerateErrorResponse(BaseModel):
    """Error response model for SQL generation."""
    error: str
    issues: Optional[list[str]] = None
    meta: Optional[Dict[str, Any]] = None


@router.post("/api/generate", 
            response_model=GenerateSuccessResponse,
            responses={
                422: {"model": GenerateErrorResponse, "description": "SQL validation failed"},
                400: {"model": GenerateErrorResponse, "description": "Bad request"},
                500: {"model": GenerateErrorResponse, "description": "Internal server error"}
            })
async def generate_sql_and_execute(
    request: GenerateRequest,
    http_request: Request
) -> Dict[str, Any]:
    """
    Generate T-SQL from natural language and execute it.
    
    This endpoint orchestrates the complete flow:
    1. Generate SQL from natural language using LLM
    2. Validate SQL through safety layer
    3. Execute SQL against the database
    4. Return paginated results with metadata
    
    Args:
        request: The generation request containing prompt and pagination
        http_request: FastAPI request object for logging
    
    Returns:
        JSON response with query results or error details
        
    Raises:
        HTTPException: For various error conditions with appropriate status codes
    """
    # Generate correlation ID for request tracking
    correlation_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    # Log request start
    logger.info(f"Starting SQL generation request [correlation_id={correlation_id}] prompt='{request.prompt[:100]}...'")
    
    try:
        # Step 1: Generate SQL from natural language
        logger.debug(f"Generating SQL [correlation_id={correlation_id}]")
        
        # Use the configured allowlist from settings
        allowed_tables = list(settings.sql_allowlist_set)
        
        sql_result: SqlGenResult = await sql_generator.generate_sql(
            prompt=request.prompt,
            page=request.page,
            page_size=request.page_size,
            allowed_tables=allowed_tables
        )
        
        # Check if SQL generation failed
        if sql_result.issues:
            logger.warning(f"SQL generation failed [correlation_id={correlation_id}]: {sql_result.issues}")
            
            # Return 422 for SQL validation failures
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "SQL_VALIDATION_FAILED",
                    "issues": sql_result.issues,
                    "meta": {
                        **sql_result.meta,
                        "correlation_id": correlation_id,
                        "prompt": request.prompt[:200] + "..." if len(request.prompt) > 200 else request.prompt
                    }
                }
            )
        
        logger.info(f"SQL generated successfully [correlation_id={correlation_id}]")
        
        # Step 2: Execute the validated SQL
        logger.debug(f"Executing SQL [correlation_id={correlation_id}]: {sql_result.sql[:200]}...")
        
        try:
            query_result: QueryResult = db_executor.execute_query(
                sql=sql_result.sql,
                timeout=settings.sql_timeout_seconds
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Request completed successfully [correlation_id={correlation_id}] "
                f"rows={query_result.row_count} time={execution_time:.3f}s"
            )
            
            # Step 3: Return successful response
            return {
                "sql": sql_result.sql,
                "columns": query_result.columns,
                "rows": query_result.rows,
                "page": request.page,
                "page_size": request.page_size,
                "meta": {
                    "correlation_id": correlation_id,
                    "validated": True,
                    "repair_attempts": sql_result.meta.get("repair_attempts", 0),
                    "generation_time_seconds": sql_result.meta.get("generation_time_seconds", 0),
                    "execution_time_seconds": query_result.execution_time_seconds,
                    "total_time_seconds": execution_time,
                    "row_count": query_result.row_count,
                    "has_more": query_result.has_more,
                    "model": sql_result.meta.get("model", "unknown")
                }
            }
            
        except ExecutionError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(
                f"SQL execution failed [correlation_id={correlation_id}] "
                f"time={execution_time:.3f}s error={e.error_code}: {e.message}"
            )
            
            # Map execution errors to appropriate HTTP status codes
            if e.error_code in ["FETCH_ERROR", "SQL_EXECUTION_ERROR"]:
                status_code = 422  # Unprocessable Entity - SQL was invalid
            elif e.error_code == "TIMEOUT_ERROR":
                status_code = 408  # Request Timeout
            else:
                status_code = 500  # Internal Server Error
            
            raise HTTPException(
                status_code=status_code,
                detail={
                    "error": e.error_code,
                    "message": e.message,
                    "meta": {
                        "correlation_id": correlation_id,
                        "sql": sql_result.sql[:200] + "..." if len(sql_result.sql) > 200 else sql_result.sql,
                        "sql_state": e.sql_state,
                        "native_error": e.native_error,
                        "total_time_seconds": execution_time
                    }
                }
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.error(
            f"Unexpected error in SQL generation [correlation_id={correlation_id}] "
            f"time={execution_time:.3f}s: {str(e)}"
        )
        
        # Return 500 for unexpected errors
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during SQL generation",
                "meta": {
                    "correlation_id": correlation_id,
                    "total_time_seconds": execution_time
                }
            }
        )


@router.get("/api/generate/health")
async def health_check():
    """Health check endpoint for the generate service."""
    try:
        # Test database connectivity
        db_healthy = db_executor.test_connection()
        
        # Test if OpenAI API key is configured
        llm_configured = settings.openai_api_key is not None and len(settings.openai_api_key.strip()) > 0
        
        status = "healthy" if db_healthy and llm_configured else "unhealthy"
        
        return {
            "status": status,
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "llm": "configured" if llm_configured else "not_configured"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
