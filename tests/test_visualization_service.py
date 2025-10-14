"""
Unit tests for visualization service.

Tests correlation matrix calculation, validation, and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from app.visualization_service import (
    calculate_correlation_matrix,
    validate_correlation_request
)


def test_calculate_correlation_matrix_success():
    """Test successful correlation matrix calculation."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [2, 4, 6, 8, 10],
        'C': [5, 4, 3, 2, 1]
    })
    
    result = calculate_correlation_matrix(df, ['A', 'B', 'C'])
    
    assert result['status'] == 'success'
    assert result['columns'] == ['A', 'B', 'C']
    assert result['correlation_matrix']['A']['B'] == pytest.approx(1.0, abs=0.01)
    assert result['correlation_matrix']['A']['C'] == pytest.approx(-1.0, abs=0.01)
    assert result['correlation_matrix']['B']['B'] == 1.0


def test_calculate_correlation_matrix_with_sampling():
    """Test correlation matrix with large dataset."""
    np.random.seed(42)
    df = pd.DataFrame({
        'X': np.random.randn(15000),
        'Y': np.random.randn(15000),
        'Z': np.random.randn(15000)
    })
    
    result = calculate_correlation_matrix(df, ['X', 'Y', 'Z'], max_rows=10000)
    
    assert result['is_sampled'] == True
    assert result['sample_size'] <= 10000
    assert result['original_size'] == 15000
    assert 'X' in result['correlation_matrix']


def test_calculate_correlation_matrix_with_missing_data():
    """Test correlation matrix with NaN values."""
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4, 5],
        'B': [2, 4, 6, np.nan, 10],
        'C': [5, 4, 3, 2, 1]
    })
    
    result = calculate_correlation_matrix(df, ['A', 'B', 'C'])
    
    assert result['status'] == 'success'
    assert result['rows_with_missing_data'] > 0
    assert result['sample_size'] < 5


def test_calculate_correlation_matrix_insufficient_data():
    """Test correlation matrix with insufficient data after NaN removal."""
    df = pd.DataFrame({
        'A': [1, np.nan, np.nan],
        'B': [np.nan, 2, np.nan]
    })
    
    with pytest.raises(ValueError, match="Insufficient data"):
        calculate_correlation_matrix(df, ['A', 'B'])


def test_validate_correlation_request_minimum_columns():
    """Test validation rejects < 2 columns."""
    df = pd.DataFrame({'A': [1, 2, 3]})
    
    validation = validate_correlation_request(df, ['A'])
    
    assert validation['valid'] == False
    assert 'at least 2' in validation['message'].lower()


def test_validate_correlation_request_maximum_columns():
    """Test validation rejects > 15 columns."""
    df = pd.DataFrame({f'col{i}': [1, 2, 3] for i in range(20)})
    columns = [f'col{i}' for i in range(16)]
    
    validation = validate_correlation_request(df, columns)
    
    assert validation['valid'] == False
    assert 'maximum 15' in validation['message'].lower()


def test_validate_correlation_request_non_numeric():
    """Test validation rejects non-numeric columns."""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['x', 'y', 'z'],
        'C': [4, 5, 6]
    })
    
    validation = validate_correlation_request(df, ['A', 'B', 'C'])
    
    assert validation['valid'] == False
    assert 'non-numeric' in validation['message'].lower()
    assert 'B' in validation['message']


def test_validate_correlation_request_missing_columns():
    """Test validation rejects non-existent columns."""
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    
    validation = validate_correlation_request(df, ['A', 'C'])
    
    assert validation['valid'] == False
    assert 'not found' in validation['message'].lower()


def test_validate_correlation_request_success():
    """Test validation accepts valid request."""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6],
        'C': [7, 8, 9]
    })
    
    validation = validate_correlation_request(df, ['A', 'B', 'C'])
    
    assert validation['valid'] == True


def test_calculate_correlation_matrix_two_columns():
    """Test correlation matrix with exactly 2 columns."""
    df = pd.DataFrame({
        'X': [1, 2, 3, 4, 5],
        'Y': [5, 4, 3, 2, 1]
    })
    
    result = calculate_correlation_matrix(df, ['X', 'Y'])
    
    assert result['status'] == 'success'
    assert len(result['columns']) == 2
    assert result['correlation_matrix']['X']['Y'] == pytest.approx(-1.0, abs=0.01)


def test_calculate_correlation_matrix_no_sampling_needed():
    """Test correlation matrix with small dataset (no sampling)."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [2, 3, 4, 5, 6]
    })
    
    result = calculate_correlation_matrix(df, ['A', 'B'], max_rows=10000)
    
    assert result['status'] == 'success'
    assert result['is_sampled'] == False
    assert result['original_size'] == 5
    assert result['sample_size'] == 5


def test_calculate_correlation_matrix_perfect_positive():
    """Test perfect positive correlation."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })
    
    result = calculate_correlation_matrix(df, ['A', 'B'])
    
    assert result['correlation_matrix']['A']['B'] == pytest.approx(1.0, abs=0.01)


def test_calculate_correlation_matrix_perfect_negative():
    """Test perfect negative correlation."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [50, 40, 30, 20, 10]
    })
    
    result = calculate_correlation_matrix(df, ['A', 'B'])
    
    assert result['correlation_matrix']['A']['B'] == pytest.approx(-1.0, abs=0.01)


def test_calculate_correlation_matrix_no_correlation():
    """Test near-zero correlation."""
    np.random.seed(42)
    df = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100)
    })
    
    result = calculate_correlation_matrix(df, ['A', 'B'])
    
    # Random data should have correlation close to 0
    assert abs(result['correlation_matrix']['A']['B']) < 0.3


def test_calculate_correlation_matrix_diagonal_ones():
    """Test that diagonal values are all 1.0."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [2, 4, 6, 8, 10],
        'C': [5, 4, 3, 2, 1]
    })
    
    result = calculate_correlation_matrix(df, ['A', 'B', 'C'])
    
    # Self-correlation should be 1.0
    assert result['correlation_matrix']['A']['A'] == 1.0
    assert result['correlation_matrix']['B']['B'] == 1.0
    assert result['correlation_matrix']['C']['C'] == 1.0


def test_calculate_correlation_matrix_symmetric():
    """Test that correlation matrix is symmetric."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [2, 4, 6, 8, 10],
        'C': [5, 4, 3, 2, 1]
    })
    
    result = calculate_correlation_matrix(df, ['A', 'B', 'C'])
    
    # Matrix should be symmetric
    assert result['correlation_matrix']['A']['B'] == result['correlation_matrix']['B']['A']
    assert result['correlation_matrix']['A']['C'] == result['correlation_matrix']['C']['A']
    assert result['correlation_matrix']['B']['C'] == result['correlation_matrix']['C']['B']
