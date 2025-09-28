"""
Integration tests for the /api/generate endpoint.

This module tests the complete end-to-end flow including:
- API endpoint behavior with various inputs
- Integration between LLM generator, validator, and database executor
- Error handling and response formatting
- Pagination and metadata handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.llm.sql_generator import SqlGenResult
from app.db.exec import QueryResult, ExecutionError
from app.validation.sql_validator import ValidationResult, ValidationIssue


client = TestClient(app)


class TestGenerateEndpoint:
    """Test cases for /api/generate endpoint."""
    
    def test_generate_success_flow(self):
        """Test successful end-to-end generation and execution."""
        request_data = {
            "prompt": "Show me the top 10 products by list price",
            "page": 1,
            "page_size": 10
        }
        
        # Mock successful LLM generation
        mock_sql_result = SqlGenResult(
            sql="SELECT TOP 10 ProductID, Name, ListPrice FROM Production.Product ORDER BY ListPrice DESC;",
            issues=[],
            meta={
                "model": "gpt-4",
                "repair_attempts": 0,
                "generation_time_seconds": 1.5,
                "validation_passed": True
            },
            correlation_id="test-correlation-id",
            generated_at=datetime.now()
        )
        
        # Mock successful database execution
        mock_query_result = QueryResult(
            rows=[
                [1, "Road-150 Red, 62", 3578.27],
                [2, "Road-150 Red, 44", 3578.27]
            ],
            columns=[
                {"name": "ProductID", "type": "int"},
                {"name": "Name", "type": "varchar"},
                {"name": "ListPrice", "type": "decimal"}
            ],
            row_count=2,
            execution_time_seconds=0.5,
            has_more=False
        )
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate, \
             patch('app.routes.generate.db_executor.execute_query') as mock_execute:
            
            mock_generate.return_value = mock_sql_result
            mock_execute.return_value = mock_query_result
            
            response = client.post("/api/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "sql" in data
            assert "columns" in data
            assert "rows" in data
            assert "page" in data
            assert "page_size" in data
            assert "meta" in data
            
            # Verify response content
            assert data["sql"] == mock_sql_result.sql
            assert data["columns"] == mock_query_result.columns
            assert data["rows"] == mock_query_result.rows
            assert data["page"] == 1
            assert data["page_size"] == 10
            
            # Verify metadata
            meta = data["meta"]
            assert meta["validated"] == True
            assert meta["repair_attempts"] == 0
            assert "correlation_id" in meta
            assert "total_time_seconds" in meta
            assert meta["row_count"] == 2
    
    def test_generate_validation_failure(self):
        """Test handling of SQL validation failures."""
        request_data = {
            "prompt": "Show me all data from secret_table",
            "page": 1,
            "page_size": 20
        }
        
        # Mock validation failure
        mock_sql_result = SqlGenResult(
            sql="SELECT * FROM secret_table;",
            issues=["Referenced objects not in allowlist: secret_table"],
            meta={
                "model": "gpt-4",
                "repair_attempts": 3,
                "generation_time_seconds": 2.5,
                "validation_passed": False
            },
            correlation_id="test-correlation-id",
            generated_at=datetime.now()
        )
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate:
            mock_generate.return_value = mock_sql_result
            
            response = client.post("/api/generate", json=request_data)
            
            assert response.status_code == 422
            data = response.json()
            
            # Verify error response structure
            assert "detail" in data
            detail = data["detail"]
            assert detail["error"] == "SQL_VALIDATION_FAILED"
            assert "issues" in detail
            assert "secret_table" in str(detail["issues"])
            
            # Verify metadata
            assert "meta" in detail
            assert "correlation_id" in detail["meta"]
    
    def test_generate_database_execution_error(self):
        """Test handling of database execution errors."""
        request_data = {
            "prompt": "Show me products",
            "page": 1,
            "page_size": 20
        }
        
        # Mock successful generation but database error
        mock_sql_result = SqlGenResult(
            sql="SELECT ProductID, Name FROM Production.Product ORDER BY ProductID OFFSET 0 ROWS FETCH NEXT 20 ROWS ONLY;",
            issues=[],
            meta={"model": "gpt-4", "validation_passed": True},
            correlation_id="test-correlation-id",
            generated_at=datetime.now()
        )
        
        mock_db_error = ExecutionError(
            error_code="SQL_EXECUTION_ERROR",
            message="Invalid column name 'Name'",
            sql_state="42S22",
            native_error=207
        )
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate, \
             patch('app.routes.generate.db_executor.execute_query') as mock_execute:
            
            mock_generate.return_value = mock_sql_result
            mock_execute.side_effect = mock_db_error
            
            response = client.post("/api/generate", json=request_data)
            
            assert response.status_code == 422
            data = response.json()
            
            # Verify error response
            assert "detail" in data
            detail = data["detail"]
            assert detail["error"] == "SQL_EXECUTION_ERROR"
            assert "Invalid column name" in detail["message"]
            
            # Verify metadata includes SQL and error details
            meta = detail["meta"]
            assert "sql" in meta
            assert meta["sql_state"] == "42S22"
            assert meta["native_error"] == 207
    
    def test_generate_invalid_request_data(self):
        """Test validation of request data."""
        test_cases = [
            # Empty prompt
            {
                "prompt": "",
                "page": 1,
                "page_size": 20
            },
            # Invalid page number
            {
                "prompt": "Show me products",
                "page": 0,
                "page_size": 20
            },
            # Invalid page size
            {
                "prompt": "Show me products",
                "page": 1,
                "page_size": 0
            },
            # Missing prompt
            {
                "page": 1,
                "page_size": 20
            },
            # Prompt too long
            {
                "prompt": "x" * 1001,
                "page": 1,
                "page_size": 20
            }
        ]
        
        for invalid_data in test_cases:
            response = client.post("/api/generate", json=invalid_data)
            assert response.status_code == 422  # Validation error
    
    def test_generate_pagination_parameters(self):
        """Test various pagination parameter combinations."""
        test_cases = [
            {"page": 1, "page_size": 10},
            {"page": 5, "page_size": 50},
            {"page": 100, "page_size": 1},
        ]
        
        # Mock successful responses
        mock_sql_result = SqlGenResult(
            sql="SELECT * FROM Production.Product ORDER BY ProductID OFFSET 0 ROWS FETCH NEXT 20 ROWS ONLY;",
            issues=[],
            meta={"model": "gpt-4", "validation_passed": True},
            correlation_id="test-id",
            generated_at=datetime.now()
        )
        
        mock_query_result = QueryResult(
            rows=[],
            columns=[],
            row_count=0,
            execution_time_seconds=0.1,
            has_more=False
        )
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate, \
             patch('app.routes.generate.db_executor.execute_query') as mock_execute:
            
            mock_generate.return_value = mock_sql_result
            mock_execute.return_value = mock_query_result
            
            for params in test_cases:
                request_data = {
                    "prompt": "Show me products",
                    **params
                }
                
                response = client.post("/api/generate", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["page"] == params["page"]
                assert data["page_size"] == params["page_size"]
    
    def test_generate_timeout_error(self):
        """Test handling of timeout errors."""
        request_data = {
            "prompt": "Complex query that times out",
            "page": 1,
            "page_size": 20
        }
        
        # Mock successful generation but timeout during execution
        mock_sql_result = SqlGenResult(
            sql="SELECT * FROM Production.Product;",
            issues=[],
            meta={"model": "gpt-4", "validation_passed": True},
            correlation_id="test-id",
            generated_at=datetime.now()
        )
        
        timeout_error = ExecutionError(
            error_code="TIMEOUT_ERROR",
            message="Query timeout after 30 seconds"
        )
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate, \
             patch('app.routes.generate.db_executor.execute_query') as mock_execute:
            
            mock_generate.return_value = mock_sql_result
            mock_execute.side_effect = timeout_error
            
            response = client.post("/api/generate", json=request_data)
            
            assert response.status_code == 408  # Request Timeout
            data = response.json()
            assert "timeout" in data["detail"]["message"].lower()
    
    def test_generate_internal_server_error(self):
        """Test handling of unexpected internal errors."""
        request_data = {
            "prompt": "Show me products",
            "page": 1,
            "page_size": 20
        }
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate:
            mock_generate.side_effect = Exception("Unexpected error")
            
            response = client.post("/api/generate", json=request_data)
            
            assert response.status_code == 500
            data = response.json()
            assert data["detail"]["error"] == "INTERNAL_SERVER_ERROR"
            assert "correlation_id" in data["detail"]["meta"]
    
    def test_generate_health_endpoint(self):
        """Test the health check endpoint."""
        with patch('app.routes.generate.db_executor.test_connection') as mock_db_test, \
             patch('app.routes.generate.settings.openai_api_key', 'test-key'):
            
            mock_db_test.return_value = True
            
            response = client.get("/api/generate/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "healthy"
            assert data["components"]["database"] == "healthy"
            assert data["components"]["llm"] == "configured"
            assert "timestamp" in data
    
    def test_generate_health_endpoint_unhealthy(self):
        """Test health endpoint when services are unhealthy."""
        with patch('app.routes.generate.db_executor.test_connection') as mock_db_test, \
             patch('app.routes.generate.settings.openai_api_key', None):
            
            mock_db_test.return_value = False
            
            response = client.get("/api/generate/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "unhealthy"
            assert data["components"]["database"] == "unhealthy"
            assert data["components"]["llm"] == "not_configured"
    
    def test_generate_correlation_id_in_logs(self):
        """Test that correlation IDs are included in response metadata."""
        request_data = {
            "prompt": "Show me products",
            "page": 1,
            "page_size": 20
        }
        
        mock_sql_result = SqlGenResult(
            sql="SELECT * FROM Production.Product;",
            issues=[],
            meta={"model": "gpt-4", "validation_passed": True},
            correlation_id="custom-correlation-id",
            generated_at=datetime.now()
        )
        
        mock_query_result = QueryResult(
            rows=[],
            columns=[],
            row_count=0,
            execution_time_seconds=0.1,
            has_more=False
        )
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate, \
             patch('app.routes.generate.db_executor.execute_query') as mock_execute:
            
            mock_generate.return_value = mock_sql_result
            mock_execute.return_value = mock_query_result
            
            response = client.post("/api/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify correlation ID is in response metadata
            assert "correlation_id" in data["meta"]
            # Note: The endpoint generates its own correlation ID, so it won't match the mock
            assert len(data["meta"]["correlation_id"]) > 0


class TestGenerateEndpointEdgeCases:
    """Test edge cases and boundary conditions for the generate endpoint."""
    
    def test_generate_with_whitespace_prompt(self):
        """Test handling of prompts with only whitespace."""
        request_data = {
            "prompt": "   \n\t  ",
            "page": 1,
            "page_size": 20
        }
        
        response = client.post("/api/generate", json=request_data)
        assert response.status_code == 422
    
    def test_generate_with_special_characters_prompt(self):
        """Test handling of prompts with special characters."""
        request_data = {
            "prompt": "Show me products with names containing 'quotes' and \"double quotes\" and <tags>",
            "page": 1,
            "page_size": 20
        }
        
        mock_sql_result = SqlGenResult(
            sql="SELECT ProductID, Name FROM Production.Product WHERE Name LIKE '%quotes%';",
            issues=[],
            meta={"validation_passed": True},
            correlation_id="test-id",
            generated_at=datetime.now()
        )
        
        mock_query_result = QueryResult(
            rows=[],
            columns=[],
            row_count=0,
            execution_time_seconds=0.1,
            has_more=False
        )
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate, \
             patch('app.routes.generate.db_executor.execute_query') as mock_execute:
            
            mock_generate.return_value = mock_sql_result
            mock_execute.return_value = mock_query_result
            
            response = client.post("/api/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "quotes" in data["sql"]
    
    def test_generate_maximum_page_size(self):
        """Test maximum page size limits."""
        request_data = {
            "prompt": "Show me products",
            "page": 1,
            "page_size": 100  # Maximum allowed
        }
        
        mock_sql_result = SqlGenResult(
            sql="SELECT * FROM Production.Product ORDER BY ProductID OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY;",
            issues=[],
            meta={"validation_passed": True},
            correlation_id="test-id",
            generated_at=datetime.now()
        )
        
        mock_query_result = QueryResult(
            rows=[],
            columns=[],
            row_count=0,
            execution_time_seconds=0.1,
            has_more=False
        )
        
        with patch('app.routes.generate.sql_generator.generate_sql') as mock_generate, \
             patch('app.routes.generate.db_executor.execute_query') as mock_execute:
            
            mock_generate.return_value = mock_sql_result
            mock_execute.return_value = mock_query_result
            
            response = client.post("/api/generate", json=request_data)
            assert response.status_code == 200
    
    def test_generate_exceeds_maximum_page_size(self):
        """Test page size exceeding maximum."""
        request_data = {
            "prompt": "Show me products",
            "page": 1,
            "page_size": 101  # Exceeds maximum
        }
        
        response = client.post("/api/generate", json=request_data)
        assert response.status_code == 422
