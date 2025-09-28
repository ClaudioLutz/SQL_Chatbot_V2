"""
FastAPI routes for visualization rendering.

This module provides the /api/render endpoint for generating secure 
visualizations from SQL result data using the sandboxed chart generation engine.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, Field, validator

from app.viz.sandbox import render_chart, ChartResult
from app.middleware import get_request_id
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["visualization"])

class RenderRequest(BaseModel):
    """Request model for chart rendering."""
    
    sql: Optional[str] = Field(
        None,
        description="SQL query that generated the data (for context)",
        max_length=10000
    )
    data: List[Dict[str, Any]] = Field(
        ...,
        description="Array of data rows to visualize"
    )
    chart: str = Field(
        "auto",
        description="Chart type: auto, bar, line, scatter, histogram, heatmap",
        pattern="^(auto|bar|line|scatter|histogram|hist|heatmap)$"
    )
    x: Optional[str] = Field(
        None,
        description="Column name for X-axis",
        max_length=100
    )
    y: Optional[str] = Field(
        None,
        description="Column name for Y-axis", 
        max_length=100
    )
    series: Optional[str] = Field(
        None,
        description="Column name for series/grouping",
        max_length=100
    )
    limit: int = Field(
        1000,
        description="Maximum number of data points to render",
        ge=1,
        le=5000
    )
    mode: str = Field(
        "spec",
        description="Rendering mode: spec (declarative) or python (code execution)",
        pattern="^(spec|python)$"
    )
    enable_python: bool = Field(
        False,
        description="Feature flag to enable python-code mode execution"
    )
    code: Optional[str] = Field(
        None,
        description="Optional Python code for custom visualization",
        max_length=50000
    )

    @validator('data')
    def validate_data_not_empty_if_provided(cls, v):
        """Validate data structure."""
        if v is not None and len(v) == 0:
            # Empty data is allowed, will return appropriate error
            pass
        return v
    
    @validator('chart')
    def normalize_chart_type(cls, v):
        """Normalize chart type names."""
        # Map common aliases
        if v == 'hist':
            return 'histogram'
        return v

class RenderResponse(BaseModel):
    """Response model for chart rendering."""
    
    success: bool = Field(..., description="Whether rendering succeeded")
    png_base64: Optional[str] = Field(None, description="Base64-encoded PNG image data")
    caption: str = Field(..., description="Descriptive caption for the chart")
    chart_type: str = Field(..., description="Actual chart type that was rendered")
    code_echo: Optional[str] = Field(None, description="Echo of generated/executed code")
    dimensions: List[int] = Field(..., description="Image dimensions [width, height]")
    data_summary: Dict[str, Any] = Field(..., description="Summary of input data")
    issues: List[str] = Field(default_factory=list, description="Warnings or non-fatal issues")
    correlation_id: str = Field(..., description="Request correlation ID for debugging")
    generated_at: str = Field(..., description="ISO timestamp of generation")

@router.post("/render", response_model=RenderResponse)
async def render_visualization(
    request: RenderRequest,
    response: Response,
    request_id: str = Depends(get_request_id)
) -> RenderResponse:
    """
    Render a visualization from data in a secure sandbox environment.
    
    This endpoint accepts SQL result data and generates charts with strict security:
    - No filesystem or network access
    - CPU and memory limits enforced
    - Headless rendering only
    - Returns base64-encoded PNG images
    
    **Security Features:**
    - Import whitelist (matplotlib, seaborn, pandas, numpy only)
    - Resource limits (10s CPU, 512MB RAM)  
    - Process isolation
    - No arbitrary code execution in 'spec' mode
    
    **Chart Types:**
    - `auto`: Auto-detect best chart type based on data structure
    - `bar`: Bar charts for categorical data
    - `line`: Line charts for time series or continuous data
    - `scatter`: Scatter plots for correlation analysis
    - `histogram`: Distribution plots for numeric data
    - `heatmap`: Correlation matrices for multiple numeric variables
    
    **Modes:**
    - `spec`: Declarative mode using data structure (recommended, safer)
    - `python`: Code execution mode (requires `code` parameter, higher risk)
    """
    logger.info(f"Chart render request received [request_id={request_id}] chart={request.chart}")
    
    # Set Cache-Control headers to prevent stale images in demos
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Limit data size for performance and security
        limited_data = request.data[:request.limit] if len(request.data) > request.limit else request.data
        
        # Log data summary for debugging
        logger.info(f"Rendering {len(limited_data)} data points [request_id={request_id}]")
        
        # Validate mode and code consistency
        if request.mode == "python" and not request.code:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Validation Error",
                    "message": "Python mode requires 'code' parameter",
                    "request_id": request_id
                }
            )
        
        if request.mode == "python":
            # Check feature flag for python-code mode
            if not request.enable_python:
                logger.warning(f"Python mode requires feature flag [request_id={request_id}]")
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "Feature Flag Required",
                        "message": "Python code execution mode requires 'enable_python' flag set to true.",
                        "request_id": request_id
                    }
                )
            
            # Python mode implementation would go here
            logger.warning(f"Python mode not yet fully implemented [request_id={request_id}]")
            raise HTTPException(
                status_code=501,
                detail={
                    "error": "Not Implemented", 
                    "message": "Python code execution mode not yet implemented. Use 'spec' mode.",
                    "request_id": request_id
                }
            )
        
        # Render chart using sandbox
        result: ChartResult = render_chart(
            data=limited_data,
            chart_type=request.chart if request.chart != "auto" else None,
            x=request.x,
            y=request.y, 
            series=request.series
        )
        
        # Map chart result to response
        if result.success:
            logger.info(f"Chart rendering successful [request_id={request_id}] [correlation_id={result.correlation_id}]")
            
            return RenderResponse(
                success=True,
                png_base64=result.image_data,
                caption=result.caption,
                chart_type=result.chart_type,
                code_echo=None,  # Not applicable in spec mode
                dimensions=list(result.dimensions),
                data_summary=result.data_summary,
                issues=result.issues,
                correlation_id=result.correlation_id,
                generated_at=result.generated_at.isoformat()
            )
        else:
            logger.error(f"Chart rendering failed [request_id={request_id}] [correlation_id={result.correlation_id}]: {result.issues}")
            
            return RenderResponse(
                success=False,
                png_base64=None,
                caption=result.caption,
                chart_type=result.chart_type,
                code_echo=None,
                dimensions=list(result.dimensions),
                data_summary=result.data_summary,
                issues=result.issues,
                correlation_id=result.correlation_id,
                generated_at=result.generated_at.isoformat()
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in chart rendering [request_id={request_id}]: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Chart rendering failed due to internal error",
                "request_id": request_id
            }
        )

@router.get("/render/health")
async def render_health_check(
    response: Response,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Health check endpoint for visualization rendering service.
    
    Performs basic validation that the rendering environment is working:
    - Matplotlib backend is properly configured
    - Security sandbox can be initialized
    - Basic chart generation works
    """
    logger.info(f"Render health check requested [request_id={request_id}]")
    
    # Set Cache-Control headers for health check too
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    
    try:
        # Test basic chart rendering with sample data
        test_data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "C", "value": 15}
        ]
        
        result = render_chart(data=test_data, chart_type="bar")
        
        if result.success:
            return {
                "status": "healthy",
                "service": "visualization-renderer",
                "backend": "matplotlib-agg",
                "sandbox": "operational",
                "test_chart": "generated",
                "request_id": request_id
            }
        else:
            logger.error(f"Health check chart generation failed [request_id={request_id}]: {result.issues}")
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "unhealthy",
                    "service": "visualization-renderer", 
                    "error": "Test chart generation failed",
                    "issues": result.issues,
                    "request_id": request_id
                }
            )
            
    except Exception as e:
        logger.error(f"Health check failed [request_id={request_id}]: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "visualization-renderer",
                "error": "Health check failed",
                "message": str(e),
                "request_id": request_id
            }
        )
