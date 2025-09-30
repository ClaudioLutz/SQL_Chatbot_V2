"""Integration tests for /api/analyze endpoint."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.fixtures.analysis_test_data import SMALL_DATASET, TOO_LARGE_DATASET, EMPTY_DATASET

client = TestClient(app)


class TestAnalyzeEndpoint:
    """Test /api/analyze endpoint."""
    
    def test_analyze_success(self):
        """Test successful analysis."""
        response = client.post("/api/analyze", json=SMALL_DATASET)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "variable_types" in data
        assert "numeric_stats" in data
        assert "cardinality" in data
        assert "missing_values" in data
        assert data["row_count"] == 10
        assert data["column_count"] == 3
    
    def test_analyze_too_large(self):
        """Test rejection of large dataset."""
        response = client.post("/api/analyze", json=TOO_LARGE_DATASET)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "too_large"
        assert "50,000 rows" in data["message"]
        assert data["row_count"] == 60000
    
    def test_analyze_insufficient_rows(self):
        """Test rejection of dataset with insufficient rows."""
        response = client.post("/api/analyze", json=EMPTY_DATASET)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "insufficient_rows"
        assert data["row_count"] == 0
    
    def test_analyze_invalid_request_missing_columns(self):
        """Test invalid request format - missing columns."""
        response = client.post("/api/analyze", json={"rows": [{"A": 1}]})
        assert response.status_code == 422  # Pydantic validation error
    
    def test_analyze_invalid_request_missing_rows(self):
        """Test invalid request format - missing rows."""
        response = client.post("/api/analyze", json={"columns": ["A"]})
        assert response.status_code == 422  # Pydantic validation error
    
    def test_analyze_empty_body(self):
        """Test empty request body."""
        response = client.post("/api/analyze", json={})
        assert response.status_code == 422
    
    def test_analyze_malformed_json(self):
        """Test malformed JSON request."""
        response = client.post(
            "/api/analyze", 
            content=b"invalid json", 
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_analyze_wrong_data_types(self):
        """Test with wrong data types."""
        invalid_data = {
            "columns": "not a list",  # should be list
            "rows": {"not": "a list"}  # should be list
        }
        response = client.post("/api/analyze", json=invalid_data)
        assert response.status_code == 422
    
    def test_analyze_with_mixed_data_types(self):
        """Test analysis with mixed data types."""
        mixed_data = {
            "columns": ["ID", "Name", "Price", "Active"],
            "rows": [
                {"ID": 1, "Name": "Item1", "Price": 10.5, "Active": True},
                {"ID": 2, "Name": "Item2", "Price": 20.0, "Active": False},
                {"ID": 3, "Name": "Item3", "Price": 15.75, "Active": True}
            ]
        }
        response = client.post("/api/analyze", json=mixed_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["row_count"] == 3
        assert data["column_count"] == 4
    
    def test_analyze_with_null_values(self):
        """Test analysis with null values."""
        null_data = {
            "columns": ["A", "B", "C"],
            "rows": [
                {"A": 1, "B": 2, "C": None},
                {"A": None, "B": 3, "C": 4},
                {"A": 5, "B": None, "C": 6}
            ]
        }
        response = client.post("/api/analyze", json=null_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # Check that missing values are properly detected
        missing_values = data["missing_values"]
        assert len(missing_values) == 3
        for col_info in missing_values:
            if col_info["column"] in ["A", "B", "C"]:
                assert col_info["null_count"] == 1
                assert col_info["null_percentage"] > 0
    
    def test_analyze_numeric_only(self):
        """Test analysis with only numeric columns."""
        numeric_data = {
            "columns": ["X", "Y", "Z"],
            "rows": [
                {"X": 1.5, "Y": 2.7, "Z": 3.14},
                {"X": 4.2, "Y": 5.8, "Z": 6.28}
            ]
        }
        response = client.post("/api/analyze", json=numeric_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["variable_types"]["numeric"] == 3
        assert data["variable_types"]["categorical"] == 0
        assert len(data["numeric_stats"]) == 3
