"""Middleware for SQL Chatbot application."""
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Callable

from .config import settings


logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs to requests for tracking."""
    
    def __init__(self, app):
        super().__init__(app)
        self.header_name = settings.request_id_header
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate or use existing request ID
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        
        # Add request ID to context
        request.state.request_id = request_id
        
        # Log request start
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params)
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers[self.header_name] = request_id
            
            # Log successful response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "method": request.method,
                    "path": request.url.path
                }
            )
            
            return response
            
        except Exception as e:
            # Log error with request ID
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e)
                }
            )
            raise


def get_request_id(request: Request) -> str:
    """Get the current request ID from request state."""
    return getattr(request.state, 'request_id', 'unknown')
