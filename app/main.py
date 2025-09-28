import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyodbc

from .config import settings
from .middleware import RequestIDMiddleware, get_request_id
from . import services
from .routes.generate import router as generate_router
from .routes.render import router as render_router

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SQL Chatbot API",
    description="Natural language to SQL query conversion API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add Request ID middleware
app.add_middleware(RequestIDMiddleware)

# Include API routers
try:
    app.include_router(generate_router)
    logger.info("Generate router registered")
except ImportError as e:
    logger.warning(f"Generate router not available: {e}")

app.include_router(render_router)
logger.info("Render router registered")


class QueryRequest(BaseModel):
    question: str


@app.get("/healthz")
async def health_check(request: Request):
    """Health check endpoint."""
    request_id = get_request_id(request)
    logger.info("Health check requested", extra={"request_id": request_id})
    
    return {
        "status": "ok",
        "service": "sql-chatbot-api",
        "request_id": request_id
    }


@app.get("/db/ping")
async def database_ping(request: Request):
    """Database connectivity check endpoint."""
    request_id = get_request_id(request)
    logger.info("Database ping requested", extra={"request_id": request_id})
    
    try:
        with pyodbc.connect(
            settings.database_connection_string,
            timeout=settings.db_timeout_seconds
        ) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS test_connection")
            result = cursor.fetchone()
            
        logger.info(
            "Database ping successful", 
            extra={"request_id": request_id}
        )
        
        return {
            "status": "ok",
            "database": "connected",
            "server": settings.db_server,
            "database_name": settings.db_name,
            "request_id": request_id
        }
        
    except Exception as e:
        logger.error(
            f"Database ping failed: {str(e)}", 
            extra={"request_id": request_id}
        )
        
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "database": "disconnected",
                "error": "Database connection failed",
                "request_id": request_id
            }
        )


@app.post("/api/query")
async def run_query(request: QueryRequest, req: Request):
    request_id = get_request_id(req)
    logger.info(
        f"Query requested: {request.question}", 
        extra={"request_id": request_id}
    )
    
    try:
        sql_query = await services.get_sql_from_gpt(request.question)
        results = services.execute_sql_query(sql_query)
        
        logger.info(
            "Query completed successfully", 
            extra={"request_id": request_id}
        )
        
        return {
            "sql_query": sql_query, 
            "results": results,
            "request_id": request_id
        }
        
    except Exception as e:
        logger.error(
            f"Query failed: {str(e)}", 
            extra={"request_id": request_id}
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Query processing failed",
                "request_id": request_id
            }
        )


app.mount("/", StaticFiles(directory="static", html=True), name="static")
