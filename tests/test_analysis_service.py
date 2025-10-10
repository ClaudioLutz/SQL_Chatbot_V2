"""Unit tests for analysis service."""
import pytest
import pandas as pd
import numpy as np
from app.analysis_service import (
    analyze_query_results,
    _validate_dataset_requirements,
    _convert_to_dataframe,
    _extract_variable_types,
    _extract_numeric_stats,
    _extract_cardinality,
    _extract_missing_values
)
from tests.fixtures.analysis_test_data import (
    SMALL_DATASET,
    LARGE_DATASET,
    TOO_LARGE_DATASET,
    NULL_DATASET,
    MIXED_DATASET,
    EMPTY_DATASET,
    SINGLE_ROW_DATASET
)


class TestAnalyzeQueryResults:
    """Test main analyze_query_results function."""
    
    def test_valid_dataset(self):
        """Test analysis with valid dataset."""
        result = analyze_query_results(
            columns=SMALL_DATASET["columns"],
            rows=SMALL_DATASET["rows"]
        )
        assert result["status"] == "success"
        assert "variable_types" in result
        assert "numeric_stats" in result
        assert "cardinality" in result
        assert "missing_values" in result
        assert result["row_count"] == 10
        assert result["column_count"] == 3
    
    def test_large_dataset_over_50k(self):
        """Test analysis with datasets > 50K rows (now supported)."""
        result = analyze_query_results(
            columns=TOO_LARGE_DATASET["columns"],
            rows=TOO_LARGE_DATASET["rows"]
        )
        assert result["status"] == "success"
        assert result["row_count"] == 60000
        assert result["column_count"] == 1
        assert "variable_types" in result
        assert "numeric_stats" in result
    
    def test_empty_dataset(self):
        """Test handling of empty dataset."""
        result = analyze_query_results(
            columns=EMPTY_DATASET["columns"],
            rows=EMPTY_DATASET["rows"]
        )
        assert result["status"] == "insufficient_rows"
        assert result["row_count"] == 0
    
    def test_single_row_dataset(self):
        """Test rejection of single row dataset."""
        result = analyze_query_results(
            columns=SINGLE_ROW_DATASET["columns"],
            rows=SINGLE_ROW_DATASET["rows"]
        )
        assert result["status"] == "insufficient_rows"
        assert result["row_count"] == 1
    
    def test_no_columns(self):
        """Test rejection of dataset with no columns."""
        result = analyze_query_results(
            columns=[],
            rows=[{"A": 1}, {"A": 2}]
        )
        assert result["status"] == "no_columns"
        assert result["column_count"] == 0
    
    def test_numeric_only(self):
        """Test analysis with only numeric columns."""
        data = {
            "columns": ["A", "B"],
            "rows": [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
        }
        result = analyze_query_results(data["columns"], data["rows"])
        assert result["status"] == "success"
        assert result["variable_types"]["numeric"] == 2
        assert len(result["numeric_stats"]) == 2
    
    def test_with_nulls(self):
        """Test analysis with missing values."""
        result = analyze_query_results(
            columns=NULL_DATASET["columns"],
            rows=NULL_DATASET["rows"]
        )
        assert result["status"] == "success"
        # Check that missing values are detected
        missing_data = result["missing_values"]
        assert any(m["null_count"] > 0 for m in missing_data)
    
    def test_mixed_types(self):
        """Test analysis with mixed data types."""
        result = analyze_query_results(
            columns=MIXED_DATASET["columns"],
            rows=MIXED_DATASET["rows"]
        )
        assert result["status"] == "success"
        var_types = result["variable_types"]
        assert var_types["numeric"] >= 1
        assert var_types["categorical"] >= 1

    def test_large_valid_dataset(self):
        """Test analysis with large but valid dataset."""
        result = analyze_query_results(
            columns=LARGE_DATASET["columns"],
            rows=LARGE_DATASET["rows"]
        )
        assert result["status"] == "success"
        assert result["row_count"] == 45000


class TestValidation:
    """Test validation functions."""
    
    def test_valid_dataset(self):
        """Test validation passes for valid dataset."""
        is_valid, error = _validate_dataset_requirements(
            columns=["A", "B"],
            rows=[{"A": 1}, {"A": 2}]
        )
        assert is_valid is True
        assert error is None
    
    def test_no_columns(self):
        """Test validation fails for no columns."""
        is_valid, error = _validate_dataset_requirements(
            columns=[],
            rows=[{"A": 1}]
        )
        assert is_valid is False
        assert error == "no_columns"
    
    def test_insufficient_rows(self):
        """Test validation fails for < 2 rows."""
        is_valid, error = _validate_dataset_requirements(
            columns=["A"],
            rows=[{"A": 1}]
        )
        assert is_valid is False
        assert error == "insufficient_rows"
    
    def test_large_row_count(self):
        """Test validation passes for > 50K rows (now unlimited)."""
        is_valid, error = _validate_dataset_requirements(
            columns=["A"],
            rows=[{"A": i} for i in range(60000)]
        )
        assert is_valid is True
        assert error is None


class TestDataExtraction:
    """Test data extraction functions."""
    
    def test_convert_to_dataframe(self):
        """Test DataFrame conversion."""
        columns = ["A", "B"]
        rows = [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
        df = _convert_to_dataframe(columns, rows)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == columns
        assert len(df) == 2
    
    def test_extract_variable_types(self):
        """Test variable type extraction."""
        df = pd.DataFrame({
            "num": [1, 2, 3],
            "cat": ["a", "b", "c"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
        })
        types = _extract_variable_types(df)
        assert types["numeric"] == 1
        assert types["categorical"] == 1
        assert types["datetime"] == 1
        assert types["other"] == 0
    
    def test_extract_numeric_stats(self):
        """Test numeric statistics extraction."""
        df = pd.DataFrame({"A": [1, 2, 3, 4, 5]})
        stats = _extract_numeric_stats(df)
        assert len(stats) == 1
        assert stats[0]["column"] == "A"
        assert stats[0]["mean"] == 3.0
        assert stats[0]["min"] == 1.0
        assert stats[0]["max"] == 5.0
        assert stats[0]["count"] == 5
    
    def test_extract_numeric_stats_with_nulls(self):
        """Test numeric statistics with null values."""
        df = pd.DataFrame({"A": [1, 2, np.nan, 4, 5]})
        stats = _extract_numeric_stats(df)
        assert len(stats) == 1
        assert stats[0]["column"] == "A"
        assert stats[0]["count"] == 4  # null values excluded from count
        assert stats[0]["mean"] == 3.0  # (1+2+4+5)/4
    
    def test_extract_numeric_stats_all_nulls(self):
        """Test numeric statistics with all null values."""
        df = pd.DataFrame({"A": [np.nan, np.nan, np.nan]})
        stats = _extract_numeric_stats(df)
        assert len(stats) == 1
        assert stats[0]["column"] == "A"
        assert stats[0]["count"] == 0
        assert stats[0]["mean"] is None
    
    def test_extract_cardinality(self):
        """Test cardinality extraction."""
        df = pd.DataFrame({
            "A": [1, 1, 2, 2, 3],
            "B": [1, 2, 3, 4, 5]
        })
        card = _extract_cardinality(df)
        assert len(card) == 2
        assert card[0]["column"] == "A"
        assert card[0]["unique_count"] == 3
        assert card[0]["total_count"] == 5
        assert card[1]["column"] == "B"
        assert card[1]["unique_count"] == 5
        assert card[1]["total_count"] == 5
    
    def test_extract_missing_values(self):
        """Test missing values extraction."""
        df = pd.DataFrame({
            "A": [1, 2, np.nan, 4, 5],
            "B": [1, 2, 3, 4, 5]
        })
        missing = _extract_missing_values(df)
        assert len(missing) == 2
        assert missing[0]["column"] == "A"
        assert missing[0]["null_count"] == 1
        assert missing[0]["null_percentage"] == 20.0
        assert missing[1]["column"] == "B"
        assert missing[1]["null_count"] == 0
        assert missing[1]["null_percentage"] == 0.0
    
    def test_extract_missing_values_all_nulls(self):
        """Test missing values with all null column."""
        df = pd.DataFrame({
            "A": [np.nan, np.nan, np.nan],
            "B": [1, 2, 3]
        })
        missing = _extract_missing_values(df)
        assert len(missing) == 2
        assert missing[0]["column"] == "A"
        assert missing[0]["null_count"] == 3
        assert missing[0]["null_percentage"] == 100.0
        assert missing[1]["column"] == "B"
        assert missing[1]["null_count"] == 0
        assert missing[1]["null_percentage"] == 0.0

    def test_no_numeric_columns(self):
        """Test behavior when there are no numeric columns."""
        df = pd.DataFrame({
            "cat1": ["a", "b", "c"],
            "cat2": ["x", "y", "z"]
        })
        stats = _extract_numeric_stats(df)
        assert stats == []
