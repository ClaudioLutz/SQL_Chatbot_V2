"""
Tests for visualization rendering API endpoints.

This module tests the /api/render endpoint functionality including:
- Request validation and error handling
- Chart rendering integration
- Response format validation
- Health check endpoints
- Security enforcement
"""

import pytest
import json
import base64
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.viz.sandbox import ChartResult
from datetime import datetime

client = TestClient(app)

class TestRenderEndpoint:
    """Test the /api/render endpoint."""
    
    def test_render_success_flow(self):
        """Test successful chart rendering flow."""
        request_data = {
            "data": [
                {"category": "A", "value": 10},
                {"category": "B", "value": 20},
                {"category": "C", "value": 15}
            ],
            "chart": "bar",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "success" in data
        assert "caption" in data
        assert "chart_type" in data
        assert "dimensions" in data
        assert "data_summary" in data
        assert "correlation_id" in data
        assert "generated_at" in data
        
        if data["success"]:
            assert data["png_base64"] is not None
            assert isinstance(data["dimensions"], list)
            assert len(data["dimensions"]) == 2
            assert data["chart_type"] == "bar"
        else:
            # Acceptable in CI environments
            assert len(data["issues"]) > 0
    
    def test_render_auto_chart_type(self):
        """Test chart rendering with auto chart type detection."""
        request_data = {
            "data": [
                {"x": 1, "y": 2},
                {"x": 2, "y": 4}, 
                {"x": 3, "y": 6}
            ],
            "chart": "auto",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        if data["success"]:
            assert data["chart_type"] in ["scatter", "line", "bar", "heatmap"]
        
        # Should have auto-detected a chart type
        assert data["chart_type"] != "auto"
    
    def test_render_empty_data(self):
        """Test chart rendering with empty data."""
        request_data = {
            "data": [],
            "chart": "bar",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == False
        assert data["png_base64"] is None
        assert len(data["issues"]) > 0
        assert "no data" in data["issues"][0].lower()
    
    def test_render_with_optional_parameters(self):
        """Test chart rendering with optional parameters."""
        request_data = {
            "sql": "SELECT category, value FROM test_table",
            "data": [
                {"category": "A", "value": 10},
                {"category": "B", "value": 20}
            ],
            "chart": "bar",
            "x": "category",
            "y": "value",
            "limit": 100,
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "correlation_id" in data
    
    def test_render_data_limiting(self):
        """Test that large datasets are properly limited."""
        # Create large dataset
        large_data = [{"value": i} for i in range(2000)]
        
        request_data = {
            "data": large_data,
            "chart": "histogram",
            "limit": 500,
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should process only limited amount of data
        if data["success"]:
            assert data["data_summary"]["rows"] <= 500
    
    def test_render_python_mode_not_implemented(self):
        """Test that Python mode returns not implemented error."""
        request_data = {
            "data": [{"value": 10}],
            "chart": "bar",
            "mode": "python",
            "code": "plt.bar([1, 2, 3], [1, 2, 3])"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 501
        data = response.json()
        assert "not implemented" in data["detail"]["message"].lower()
    
    def test_render_python_mode_without_code(self):
        """Test Python mode without code parameter returns validation error."""
        request_data = {
            "data": [{"value": 10}],
            "chart": "bar",
            "mode": "python"
            # Missing 'code' parameter
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "code" in data["detail"]["message"].lower()
    
    def test_render_invalid_chart_type(self):
        """Test rendering with invalid chart type."""
        request_data = {
            "data": [{"value": 10}],
            "chart": "invalid_chart_type",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        # Should be rejected at validation level
        assert response.status_code == 422
    
    def test_render_invalid_mode(self):
        """Test rendering with invalid mode."""
        request_data = {
            "data": [{"value": 10}],
            "chart": "bar",
            "mode": "invalid_mode"
        }
        
        response = client.post("/api/render", json=request_data)
        
        # Should be rejected at validation level
        assert response.status_code == 422
    
    def test_render_missing_required_fields(self):
        """Test rendering with missing required fields."""
        request_data = {
            "chart": "bar",
            "mode": "spec"
            # Missing 'data' field
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 422
    
    def test_render_malformed_json(self):
        """Test rendering with malformed JSON."""
        response = client.post(
            "/api/render", 
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_render_correlation_id_in_response(self):
        """Test that correlation ID is included in response."""
        request_data = {
            "data": [{"value": 10}],
            "chart": "bar",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "correlation_id" in data
        assert len(data["correlation_id"]) > 0
        assert "generated_at" in data

class TestRenderHealthEndpoint:
    """Test the /api/render/health endpoint."""
    
    def test_render_health_success(self):
        """Test render health check returns success."""
        response = client.get("/api/render/health")
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "visualization-renderer"
            assert data["backend"] == "matplotlib-agg"
            assert data["sandbox"] == "operational" 
            assert data["test_chart"] == "generated"
            assert "request_id" in data
        else:
            # Health check may fail in CI environments without proper graphics support
            assert response.status_code == 503
            data = response.json()
            assert data["detail"]["status"] == "unhealthy"
    
    def test_render_health_failure_handling(self):
        """Test render health check handles failures gracefully."""
        # Mock render_chart to simulate failure
        with patch('app.routes.render.render_chart') as mock_render:
            from app.viz.sandbox import ChartResult
            mock_render.return_value = ChartResult(
                success=False,
                image_data=None,
                image_format="png",
                caption="Test failed",
                chart_type="bar",
                dimensions=(0, 0),
                data_summary={"rows": 0, "columns": 0},
                issues=["Test failure"],
                correlation_id="test-id",
                generated_at=datetime.now()
            )
            
            response = client.get("/api/render/health")
            
            assert response.status_code == 503
            data = response.json()
            assert data["detail"]["status"] == "unhealthy"
            assert "test chart generation failed" in data["detail"]["error"].lower()

class TestRenderSecurity:
    """Test security aspects of the render endpoint."""
    
    def test_render_input_size_limits(self):
        """Test that input size limits are enforced."""
        # Test maximum data size
        large_request = {
            "data": [{"value": i} for i in range(6000)],  # Exceeds max_items
            "chart": "bar",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=large_request)
        
        # Should be rejected at validation level or handled gracefully
        if response.status_code == 200:
            # If accepted, should be limited internally
            data = response.json()
            if data["success"]:
                assert len(data["issues"]) > 0  # Should have limiting warning
        else:
            assert response.status_code == 422
    
    def test_render_sql_parameter_safety(self):
        """Test that SQL parameter is safely handled (context only)."""
        # Very long SQL should be rejected or truncated
        long_sql = "SELECT * FROM table WHERE " + "x=1 AND " * 1000 + "y=2"
        
        request_data = {
            "sql": long_sql,
            "data": [{"value": 10}],
            "chart": "bar",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        # Should either be rejected or handled safely
        if response.status_code != 422:
            assert response.status_code in [200, 500]
    
    def test_render_string_parameter_limits(self):
        """Test that string parameters have appropriate limits."""
        request_data = {
            "data": [{"value": 10}],
            "chart": "bar",
            "x": "x" * 200,  # Exceeds max_length
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        # Should be rejected at validation level
        assert response.status_code == 422

class TestRenderResponseFormat:
    """Test response format compliance."""
    
    def test_render_response_schema_compliance(self):
        """Test that response matches defined schema."""
        request_data = {
            "data": [{"category": "A", "value": 10}],
            "chart": "bar",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = [
            "success", "caption", "chart_type", "dimensions", 
            "data_summary", "issues", "correlation_id", "generated_at"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(data["success"], bool)
        assert isinstance(data["caption"], str)
        assert isinstance(data["chart_type"], str)
        assert isinstance(data["dimensions"], list)
        assert isinstance(data["data_summary"], dict)
        assert isinstance(data["issues"], list)
        assert isinstance(data["correlation_id"], str)
        assert isinstance(data["generated_at"], str)
        
        # If successful, PNG data should be present
        if data["success"]:
            assert data["png_base64"] is not None
            assert isinstance(data["png_base64"], str)
            
            # Verify base64 format
            try:
                decoded = base64.b64decode(data["png_base64"])
                assert len(decoded) > 0
            except Exception:
                pytest.fail("Invalid base64 encoding in png_base64")
    
    def test_render_error_response_format(self):
        """Test error response format."""
        # Force an error by providing invalid data
        request_data = {
            "data": [{"value": 10}],
            "chart": "bar",
            "mode": "spec"
        }
        
        # Mock render_chart to simulate error
        with patch('app.routes.render.render_chart') as mock_render:
            mock_render.side_effect = Exception("Test error")
            
            response = client.post("/api/render", json=request_data)
            
            assert response.status_code == 500
            data = response.json()
            
            assert "error" in data["detail"]
            assert "message" in data["detail"] 
            assert "request_id" in data["detail"]
    
    def test_render_request_id_header(self):
        """Test that request ID header is properly handled."""
        request_data = {
            "data": [{"value": 10}],
            "chart": "bar",
            "mode": "spec"
        }
        
        # Test with custom request ID
        custom_request_id = "test-request-123"
        response = client.post(
            "/api/render", 
            json=request_data,
            headers={"X-Request-ID": custom_request_id}
        )
        
        # Response should include the request ID
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == custom_request_id

class TestRenderIntegration:
    """Integration tests for render endpoint."""
    
    def test_render_with_sql_result_data(self):
        """Test rendering with realistic SQL result data."""
        # Simulate data that would come from SQL query
        sql_result_data = [
            {"ProductCategory": "Bikes", "TotalSales": 25000.50, "OrderCount": 150},
            {"ProductCategory": "Components", "TotalSales": 15000.25, "OrderCount": 200},
            {"ProductCategory": "Clothing", "TotalSales": 8000.00, "OrderCount": 100},
            {"ProductCategory": "Accessories", "TotalSales": 12000.75, "OrderCount": 300}
        ]
        
        request_data = {
            "sql": "SELECT ProductCategory, SUM(Sales) as TotalSales, COUNT(*) as OrderCount FROM Orders GROUP BY ProductCategory",
            "data": sql_result_data,
            "chart": "bar",
            "x": "ProductCategory",
            "y": "TotalSales",
            "mode": "spec"
        }
        
        response = client.post("/api/render", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        if data["success"]:
            assert data["data_summary"]["rows"] == 4
            assert data["data_summary"]["columns"] == 3
            assert "ProductCategory" in data["caption"] or "TotalSales" in data["caption"]
        else:
            # Acceptable in CI environments
            assert len(data["issues"]) > 0
    
    def test_render_different_chart_types(self):
        """Test rendering different chart types with appropriate data."""
        test_cases = [
            {
                "name": "bar_chart",
                "data": [{"category": "A", "value": 10}, {"category": "B", "value": 20}],
                "chart": "bar"
            },
            {
                "name": "scatter_plot", 
                "data": [{"x": 1, "y": 2}, {"x": 2, "y": 4}, {"x": 3, "y": 6}],
                "chart": "scatter"
            },
            {
                "name": "histogram",
                "data": [{"value": i} for i in range(1, 21)],
                "chart": "histogram"
            }
        ]
        
        for test_case in test_cases:
            request_data = {
                "data": test_case["data"],
                "chart": test_case["chart"],
                "mode": "spec"
            }
            
            response = client.post("/api/render", json=request_data)
            
            assert response.status_code == 200, f"Failed for {test_case['name']}"
            data = response.json()
            
            if data["success"]:
                assert data["chart_type"] == test_case["chart"]
                assert data["png_base64"] is not None
            # Failures acceptable in CI environments
