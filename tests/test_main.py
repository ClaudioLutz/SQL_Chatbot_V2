"""Unit tests for main FastAPI application."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pyodbc

from app.main import app
from app.config import settings


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check_success(self):
        """Test /healthz endpoint returns success."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "sql-chatbot-api"
        assert "request_id" in data
        assert "X-Request-ID" in response.headers
    
    def test_health_check_has_request_id_header(self):
        """Test /healthz endpoint includes request ID in headers."""
        response = client.get("/healthz")
        
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert request_id == response.json()["request_id"]
    
    @patch('pyodbc.connect')
    def test_database_ping_success(self, mock_connect):
        """Test /db/ping endpoint returns success when database is accessible."""
        # Mock successful database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        response = client.get("/db/ping")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"
        assert data["server"] == settings.db_server
        assert data["database_name"] == settings.db_name
        assert "request_id" in data
        
        # Verify database connection was attempted
        mock_connect.assert_called_once_with(settings.database_connection_string)
        mock_cursor.execute.assert_called_once_with("SELECT 1 AS test_connection")
    
    @patch('pyodbc.connect')
    def test_database_ping_failure(self, mock_connect):
        """Test /db/ping endpoint returns error when database is inaccessible."""
        # Mock database connection failure
        mock_connect.side_effect = pyodbc.Error("Connection failed")
        
        response = client.get("/db/ping")
        
        assert response.status_code == 503
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["database"] == "disconnected"
        assert data["error"] == "Database connection failed"
        assert "request_id" in data


class TestMiddleware:
    """Test middleware functionality."""
    
    def test_request_id_middleware_generates_id(self):
        """Test that Request ID middleware generates unique IDs."""
        response1 = client.get("/healthz")
        response2 = client.get("/healthz")
        
        assert "X-Request-ID" in response1.headers
        assert "X-Request-ID" in response2.headers
        assert response1.headers["X-Request-ID"] != response2.headers["X-Request-ID"]
    
    def test_request_id_middleware_preserves_existing_id(self):
        """Test that Request ID middleware preserves existing request IDs."""
        custom_request_id = "test-request-123"
        response = client.get("/healthz", headers={"X-Request-ID": custom_request_id})
        
        assert response.headers["X-Request-ID"] == custom_request_id
        assert response.json()["request_id"] == custom_request_id
    
    def test_cors_headers_present(self):
        """Test that CORS headers are properly set."""
        response = client.options("/healthz", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestConfiguration:
    """Test configuration management."""
    
    def test_settings_loaded(self):
        """Test that settings are properly loaded."""
        assert settings.db_server is not None
        assert settings.db_port == 1433
        assert settings.db_name == "AdventureWorks2022"
        assert settings.db_encrypt == "yes"
    
    def test_database_connection_string_format(self):
        """Test that database connection string is properly formatted."""
        conn_str = settings.database_connection_string
        
        assert "ODBC Driver 18 for SQL Server" in conn_str
        assert f"Server={settings.db_server},{settings.db_port}" in conn_str
        assert f"Database={settings.db_name}" in conn_str
        assert f"Uid={settings.db_user}" in conn_str
        assert f"Encrypt={settings.db_encrypt}" in conn_str
        assert f"TrustServerCertificate={settings.db_trust_server_cert}" in conn_str


class TestErrorHandling:
    """Test error handling in endpoints."""
    
    @patch('app.main.services.get_sql_from_gpt')
    @patch('app.main.services.execute_sql_query')
    def test_query_endpoint_error_handling(self, mock_execute, mock_gpt):
        """Test /api/query endpoint error handling."""
        # Mock OpenAI service failure
        mock_gpt.side_effect = Exception("OpenAI service unavailable")
        
        response = client.post("/api/query", json={"question": "test question"})
        
        assert response.status_code == 500
        data = response.json()["detail"]
        assert data["error"] == "Query processing failed"
        assert "request_id" in data
    
    def test_invalid_request_body(self):
        """Test /api/query endpoint with invalid request body."""
        response = client.post("/api/query", json={})
        
        assert response.status_code == 422  # Validation error
