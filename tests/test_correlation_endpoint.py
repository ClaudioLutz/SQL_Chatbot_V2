"""
Integration tests for correlation matrix API endpoint.

Tests the FastAPI endpoint with various scenarios and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_correlation_matrix_endpoint_success():
    """Test successful correlation matrix generation."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": [
            {"A": 1, "B": 2, "C": 3},
            {"A": 2, "B": 4, "C": 6},
            {"A": 3, "B": 6, "C": 9}
        ],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "correlation_matrix" in data
    assert "A" in data["correlation_matrix"]
    assert data["correlation_matrix"]["A"]["A"] == 1.0


def test_correlation_matrix_endpoint_large_dataset():
    """Test with dataset requiring sampling."""
    rows = [{"A": i, "B": i*2, "C": i*3} for i in range(50000)]
    
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": rows,
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_sampled"] == True
    assert data["sample_size"] <= 10000


def test_correlation_matrix_endpoint_validation_too_few_columns():
    """Test endpoint rejects < 2 columns."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A"],
        "rows": [{"A": 1}, {"A": 2}],
        "maxRows": 10000
    })
    
    assert response.status_code == 422  # Pydantic validation


def test_correlation_matrix_endpoint_validation_too_many_columns():
    """Test endpoint rejects > 15 columns."""
    columns = [f"col{i}" for i in range(16)]
    rows = [{col: i for col in columns} for i in range(10)]
    
    response = client.post("/api/correlation-matrix", json={
        "columns": columns,
        "rows": rows,
        "maxRows": 10000
    })
    
    assert response.status_code == 422  # Pydantic validation


def test_correlation_matrix_endpoint_processing_time():
    """Test endpoint includes processing time."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B"],
        "rows": [{"A": i, "B": i*2} for i in range(1000)],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "processing_time" in data
    assert isinstance(data["processing_time"], (int, float))


def test_correlation_matrix_endpoint_two_columns():
    """Test with minimum number of columns (2)."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["X", "Y"],
        "rows": [
            {"X": 1, "Y": 5},
            {"X": 2, "Y": 4},
            {"X": 3, "Y": 3},
            {"X": 4, "Y": 2},
            {"X": 5, "Y": 1}
        ],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["columns"]) == 2
    assert abs(data["correlation_matrix"]["X"]["Y"] + 1.0) < 0.01  # Perfect negative correlation


def test_correlation_matrix_endpoint_fifteen_columns():
    """Test with maximum number of columns (15)."""
    columns = [f"col{i}" for i in range(15)]
    rows = [{col: i for col in columns} for i in range(100)]
    
    response = client.post("/api/correlation-matrix", json={
        "columns": columns,
        "rows": rows,
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["columns"]) == 15


def test_correlation_matrix_endpoint_non_numeric_columns():
    """Test endpoint handles non-numeric columns gracefully."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": [
            {"A": 1, "B": "text", "C": 3},
            {"A": 2, "B": "data", "C": 6}
        ],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "non-numeric" in data["message"].lower()


def test_correlation_matrix_endpoint_missing_columns():
    """Test endpoint handles missing columns."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "NonExistent"],
        "rows": [
            {"A": 1, "B": 2},
            {"A": 2, "B": 4}
        ],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()


def test_correlation_matrix_endpoint_with_nan_values():
    """Test endpoint handles NaN values correctly."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": [
            {"A": 1, "B": 2, "C": 3},
            {"A": 2, "B": None, "C": 6},
            {"A": 3, "B": 6, "C": 9},
            {"A": 4, "B": 8, "C": None},
            {"A": 5, "B": 10, "C": 15}
        ],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["rows_with_missing_data"] > 0


def test_correlation_matrix_endpoint_default_max_rows():
    """Test endpoint uses default maxRows of 10000."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B"],
        "rows": [{"A": i, "B": i*2} for i in range(100)]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_correlation_matrix_endpoint_custom_max_rows():
    """Test endpoint respects custom maxRows."""
    rows = [{"A": i, "B": i*2, "C": i*3} for i in range(20000)]
    
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": rows,
        "maxRows": 5000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_sampled"] == True
    assert data["sample_size"] <= 5000


def test_correlation_matrix_endpoint_perfect_correlation():
    """Test with perfect positive correlation."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B"],
        "rows": [
            {"A": 1, "B": 10},
            {"A": 2, "B": 20},
            {"A": 3, "B": 30},
            {"A": 4, "B": 40},
            {"A": 5, "B": 50}
        ],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert abs(data["correlation_matrix"]["A"]["B"] - 1.0) < 0.01


def test_correlation_matrix_endpoint_metadata():
    """Test endpoint returns all expected metadata."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": [{"A": i, "B": i*2, "C": i+5} for i in range(100)],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "status" in data
    assert "correlation_matrix" in data
    assert "columns" in data
    assert "is_sampled" in data
    assert "sample_size" in data
    assert "original_size" in data
    assert "rows_with_missing_data" in data
    assert "processing_time" in data


def test_correlation_matrix_endpoint_empty_rows():
    """Test endpoint handles empty rows array."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B"],
        "rows": [],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"


def test_correlation_matrix_endpoint_single_row():
    """Test endpoint handles single row (insufficient data)."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B"],
        "rows": [{"A": 1, "B": 2}],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "insufficient" in data["message"].lower()


def test_correlation_matrix_endpoint_performance_small_dataset():
    """Test endpoint performance with small dataset."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": [{"A": i, "B": i*2, "C": i*3} for i in range(1000)],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    # Should complete quickly (under 1 second)
    assert data["processing_time"] < 1.0


def test_correlation_matrix_endpoint_symmetric_matrix():
    """Test that returned matrix is symmetric."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": [{"A": i, "B": i*2, "C": i+5} for i in range(50)],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    matrix = data["correlation_matrix"]
    
    # Check symmetry
    assert matrix["A"]["B"] == matrix["B"]["A"]
    assert matrix["A"]["C"] == matrix["C"]["A"]
    assert matrix["B"]["C"] == matrix["C"]["B"]


def test_correlation_matrix_endpoint_diagonal_ones():
    """Test that diagonal values are 1.0."""
    response = client.post("/api/correlation-matrix", json={
        "columns": ["A", "B", "C"],
        "rows": [{"A": i, "B": i*2, "C": i+5} for i in range(50)],
        "maxRows": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    matrix = data["correlation_matrix"]
    
    # Check diagonal
    assert matrix["A"]["A"] == 1.0
    assert matrix["B"]["B"] == 1.0
    assert matrix["C"]["C"] == 1.0
