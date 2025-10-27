"""
Tests for bar chart aggregation functionality (Story BCA-001).

Tests the prepare_bar_chart_data() and detect_bar_chart_aggregation_need()
functions in visualization_service.py.
"""

import pytest
import pandas as pd
import time
from app.visualization_service import (
    prepare_bar_chart_data,
    detect_bar_chart_aggregation_need
)


class TestBarChartAggregation:
    """Test suite for bar chart aggregation functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset with duplicate categories."""
        return pd.DataFrame({
            'Status': ['Active', 'Active', 'Active', 'Pending', 'Pending', 
                      'Completed', 'Completed', 'Cancelled'],
            'Amount': [100, 200, 150, 300, 250, 400, 350, 50]
        })
    
    def test_count_aggregation_no_y_column(self, sample_data):
        """Test frequency count when Y-column is None."""
        result = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column=None,
            aggregation='auto'
        )
        
        assert result['aggregation'] == 'count'
        assert len(result['categories']) == 4  # 4 unique statuses
        assert result['chart_title'] == 'Frequency Distribution of Status'
        assert result['y_axis_label'] == 'Count'
        assert result['rows_aggregated'] == 8
        assert result['categories_shown'] == 4
        # Verify sorted by count descending
        assert result['categories'][0] == 'Active'  # 3 occurrences
        assert result['values'][0] == 3
    
    def test_sum_aggregation_with_numeric_y(self, sample_data):
        """Test SUM aggregation with numeric Y-column."""
        result = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column='Amount',
            aggregation='auto'
        )
        
        assert result['aggregation'] == 'sum'
        assert result['chart_title'] == 'Total Amount by Status'
        assert result['y_axis_label'] == 'Total Amount'
        # Verify calculations
        active_total = 100 + 200 + 150  # 450
        active_idx = result['categories'].index('Active')
        assert result['values'][active_idx] == 450
    
    def test_avg_aggregation(self, sample_data):
        """Test AVG aggregation."""
        result = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column='Amount',
            aggregation='avg'
        )
        
        assert result['aggregation'] == 'avg'
        assert result['y_axis_label'] == 'Average Amount'
        # Active average: (100 + 200 + 150) / 3 = 150
        active_idx = result['categories'].index('Active')
        active_avg = result['values'][active_idx]
        assert abs(active_avg - 150) < 0.01
    
    def test_min_max_aggregation(self, sample_data):
        """Test MIN and MAX aggregation."""
        result_min = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column='Amount',
            aggregation='min'
        )
        
        result_max = prepare_bar_chart_data(
            df=sample_data,
            x_column='Status',
            y_column='Amount',
            aggregation='max'
        )
        
        assert result_min['aggregation'] == 'min'
        assert result_max['aggregation'] == 'max'
        
        # Active min should be 100, max should be 200
        active_idx_min = result_min['categories'].index('Active')
        active_idx_max = result_max['categories'].index('Active')
        assert result_min['values'][active_idx_min] == 100
        assert result_max['values'][active_idx_max] == 200
    
    def test_top_50_limiting(self):
        """Test that categories are limited to top 50."""
        # Create dataset with 200 unique categories
        data = pd.DataFrame({
            'Category': [f'Cat_{i}' for i in range(200) for _ in range(10)],
            'Value': [i * 10 for i in range(200) for _ in range(10)]
        })
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='Category',
            y_column='Value',
            aggregation='sum',
            max_categories=50
        )
        
        assert result['categories_shown'] == 50
        assert result['total_categories'] == 200
        # Verify sorted by value descending
        assert result['values'][0] > result['values'][1]
    
    def test_null_value_removal(self):
        """Test that NULL values are handled correctly."""
        data = pd.DataFrame({
            'Status': ['Active', None, 'Pending', 'Active', None],
            'Amount': [100, 200, 300, 150, 250]
        })
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='Status',
            y_column=None,
            aggregation='count'
        )
        
        assert len(result['categories']) == 2  # Only Active and Pending
        assert None not in result['categories']
        assert result['rows_aggregated'] == 5  # Original count
        assert result['categories_shown'] == 2  # After NULL removal
    
    def test_single_category(self):
        """Test handling of single category."""
        data = pd.DataFrame({
            'Status': ['Active'] * 1000,
            'Amount': list(range(1000))
        })
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='Status',
            y_column='Amount',
            aggregation='sum'
        )
        
        assert len(result['categories']) == 1
        assert result['categories'][0] == 'Active'
        assert result['rows_aggregated'] == 1000
        # Sum of 0 to 999
        assert result['values'][0] == sum(range(1000))
    
    def test_all_unique_categories(self):
        """Test when all categories are unique (no aggregation needed)."""
        data = pd.DataFrame({
            'ID': [f'ID_{i}' for i in range(10)],
            'Value': list(range(10))
        })
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='ID',
            y_column='Value',
            aggregation='sum'
        )
        
        assert result['categories_shown'] == 10
        assert result['total_categories'] == 10
        assert result['rows_aggregated'] == 10
        # Values should be unchanged (no aggregation occurred)
        assert sorted(result['values']) == list(range(10))
    
    def test_performance_large_dataset(self):
        """Test performance with 1M rows."""
        # Create 1M row dataset with 8 unique categories
        data = pd.DataFrame({
            'Category': [f'Cat_{i % 8}' for i in range(1000000)],
            'Value': list(range(1000000))
        })
        
        start_time = time.time()
        result = prepare_bar_chart_data(
            df=data,
            x_column='Category',
            y_column='Value',
            aggregation='sum'
        )
        elapsed = time.time() - start_time
        
        assert elapsed < 0.5  # Must complete in <500ms
        assert result['categories_shown'] == 8
        assert result['rows_aggregated'] == 1000000
    
    def test_detect_aggregation_need(self):
        """Test aggregation need detection."""
        data_with_dupes = pd.DataFrame({
            'Status': ['A', 'A', 'B', 'B']
        })
        
        data_unique = pd.DataFrame({
            'ID': ['1', '2', '3', '4']
        })
        
        result_dupes = detect_bar_chart_aggregation_need(
            df=data_with_dupes,
            x_column='Status'
        )
        
        result_unique = detect_bar_chart_aggregation_need(
            df=data_unique,
            x_column='ID'
        )
        
        assert result_dupes['needs_aggregation'] is True
        assert result_unique['needs_aggregation'] is False
        assert result_dupes['duplication_ratio'] == 2.0  # 4 rows / 2 unique
        assert result_unique['duplication_ratio'] == 1.0  # 4 rows / 4 unique
    
    def test_invalid_aggregation_method(self, sample_data):
        """Test error handling for invalid aggregation method."""
        with pytest.raises(ValueError, match="Unsupported aggregation method"):
            prepare_bar_chart_data(
                df=sample_data,
                x_column='Status',
                y_column='Amount',
                aggregation='invalid_method'
            )
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        data = pd.DataFrame({'Status': [], 'Amount': []})
        
        result = prepare_bar_chart_data(
            df=data,
            x_column='Status',
            y_column=None,
            aggregation='count'
        )
        
        assert result['categories_shown'] == 0
        assert result['rows_aggregated'] == 0
        assert len(result['categories']) == 0
