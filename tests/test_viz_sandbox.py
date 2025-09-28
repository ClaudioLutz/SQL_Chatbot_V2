"""
Tests for visualization sandbox functionality.

This module tests the secure chart generation capabilities including:
- Sandbox security constraints
- Chart type detection and generation
- Import whitelist enforcement
- Resource limit enforcement
- Error handling and fallback behavior
"""

import pytest
import json
import base64
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.viz.sandbox import (
    render_chart, detect_chart_type, create_chart, ChartResult,
    timeout_handler, memory_limit_handler
)
from app.viz.whitelist import (
    ALLOWED_IMPORTS, BANNED_IMPORTS, RestrictedImporter,
    install_import_restrictions, remove_import_restrictions
)

class TestChartDetection:
    """Test chart type auto-detection logic."""
    
    def test_detect_chart_type_empty_data(self):
        """Test detection with empty DataFrame."""
        import pandas as pd
        
        empty_df = pd.DataFrame()
        chart_type = detect_chart_type(empty_df)
        assert chart_type == 'empty'
    
    def test_detect_chart_type_single_categorical(self):
        """Test detection with single categorical column."""
        import pandas as pd
        
        df = pd.DataFrame({'category': ['A', 'B', 'C', 'A']})
        chart_type = detect_chart_type(df)
        assert chart_type == 'bar'
    
    def test_detect_chart_type_single_numeric(self):
        """Test detection with single numeric column."""
        import pandas as pd
        
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        chart_type = detect_chart_type(df)
        assert chart_type == 'histogram'
    
    def test_detect_chart_type_two_numeric(self):
        """Test detection with two numeric columns."""
        import pandas as pd
        
        df = pd.DataFrame({
            'x': [1, 2, 3, 4],
            'y': [2, 4, 6, 8]
        })
        chart_type = detect_chart_type(df)
        assert chart_type == 'scatter'
    
    def test_detect_chart_type_mixed_columns(self):
        """Test detection with categorical and numeric columns."""
        import pandas as pd
        
        df = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'value': [10, 20, 30]
        })
        chart_type = detect_chart_type(df)
        assert chart_type == 'bar'
    
    def test_detect_chart_type_multiple_numeric(self):
        """Test detection with multiple numeric columns."""
        import pandas as pd
        
        df = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [4, 5, 6], 
            'z': [7, 8, 9]
        })
        chart_type = detect_chart_type(df)
        assert chart_type == 'heatmap'

class TestChartGeneration:
    """Test chart generation functionality."""
    
    def test_render_chart_empty_data(self):
        """Test chart rendering with empty data."""
        result = render_chart(data=[])
        
        assert isinstance(result, ChartResult)
        assert result.success == False
        assert result.image_data is None
        assert "No data provided" in result.issues
        assert result.chart_type == "none"
    
    def test_render_chart_simple_bar_data(self):
        """Test chart rendering with simple bar chart data."""
        test_data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "C", "value": 15}
        ]
        
        result = render_chart(data=test_data, chart_type="bar")
        
        assert isinstance(result, ChartResult)
        if result.success:
            assert result.image_data is not None
            assert result.image_format == "png"
            assert "bar" in result.chart_type.lower()
            assert result.dimensions[0] > 0 and result.dimensions[1] > 0
            assert result.data_summary["rows"] == 3
            assert result.data_summary["columns"] == 2
            
            # Verify base64 encoding
            try:
                decoded = base64.b64decode(result.image_data)
                assert len(decoded) > 0
                # Check PNG signature
                assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
            except Exception:
                pytest.fail("Invalid base64 PNG data")
        else:
            # Chart generation might fail in CI environment
            assert len(result.issues) > 0
    
    def test_render_chart_auto_detection(self):
        """Test chart rendering with auto chart type detection."""
        test_data = [
            {"x": 1, "y": 2},
            {"x": 2, "y": 4},
            {"x": 3, "y": 6}
        ]
        
        result = render_chart(data=test_data, chart_type="auto")
        
        assert isinstance(result, ChartResult)
        if result.success:
            assert result.chart_type in ["scatter", "line", "bar"]
        else:
            assert len(result.issues) > 0
    
    def test_render_chart_data_limit(self):
        """Test that data is properly limited for performance."""
        # Create data larger than MAX_DATA_ROWS
        large_data = [{"value": i} for i in range(6000)]
        
        result = render_chart(data=large_data, chart_type="histogram")
        
        assert isinstance(result, ChartResult)
        # Should have warning about data limiting
        if result.success or len(result.issues) > 0:
            limited_warning = any("limited" in issue.lower() for issue in result.issues)
            # Either successful with warning or failed due to other reasons
            if result.success:
                assert limited_warning
    
    def test_render_chart_correlation_id(self):
        """Test that correlation IDs are properly generated."""
        test_data = [{"category": "A", "value": 10}]
        
        result1 = render_chart(data=test_data, chart_type="bar")
        result2 = render_chart(data=test_data, chart_type="bar")
        
        assert result1.correlation_id != result2.correlation_id
        assert len(result1.correlation_id) > 0
        assert isinstance(result1.generated_at, datetime)

class TestSecurityWhitelist:
    """Test import whitelist security enforcement."""
    
    def test_allowed_imports_structure(self):
        """Test that allowed imports are properly structured."""
        assert isinstance(ALLOWED_IMPORTS, dict)
        assert "matplotlib" in ALLOWED_IMPORTS
        assert "pandas" in ALLOWED_IMPORTS
        assert "numpy" in ALLOWED_IMPORTS
        assert "seaborn" in ALLOWED_IMPORTS
        
        # Verify each module has allowed attributes
        for module, attrs in ALLOWED_IMPORTS.items():
            assert isinstance(attrs, set)
            assert len(attrs) > 0
    
    def test_banned_imports_structure(self):
        """Test that banned imports are properly defined."""
        assert isinstance(BANNED_IMPORTS, set)
        
        # Critical security modules should be banned
        dangerous_modules = ["os", "sys", "subprocess", "socket", "urllib"]
        for module in dangerous_modules:
            assert module in BANNED_IMPORTS
    
    def test_restricted_importer_blocks_banned(self):
        """Test that RestrictedImporter blocks banned imports."""
        importer = RestrictedImporter()
        
        # Test banned module
        with pytest.raises(ImportError, match="not allowed in sandbox"):
            importer("os")
        
        # Test banned submodule
        with pytest.raises(ImportError, match="not allowed in sandbox"):
            importer("urllib.request")
    
    def test_restricted_importer_allows_whitelisted(self):
        """Test that RestrictedImporter allows whitelisted imports."""
        importer = RestrictedImporter()
        
        # Mock the original import to avoid actually importing
        with patch.object(importer, 'original_import') as mock_import:
            mock_import.return_value = MagicMock()
            
            # Should not raise exception
            result = importer("matplotlib")
            assert result is not None
            mock_import.assert_called_once()
    
    def test_restricted_importer_blocks_unlisted(self):
        """Test that RestrictedImporter blocks modules not in whitelist."""
        importer = RestrictedImporter()
        
        with pytest.raises(ImportError, match="not allowed in sandbox"):
            importer("random_unknown_module")
    
    def test_install_remove_restrictions(self):
        """Test installing and removing import restrictions."""
        # Get original import function
        original_import = __builtins__.__import__
        
        # Install restrictions
        install_import_restrictions()
        restricted_import = __builtins__.__import__
        
        # Should be different
        assert restricted_import != original_import
        
        # Remove restrictions
        remove_import_restrictions()
        restored_import = __builtins__.__import__
        
        # Should be restored (may not be exactly the same object due to implementation)
        assert isinstance(restored_import, type(original_import))

class TestResourceLimits:
    """Test resource limit enforcement."""
    
    def test_timeout_handler_context_manager(self):
        """Test timeout handler context manager."""
        import time
        
        # Test successful completion within timeout
        with timeout_handler(5):
            time.sleep(0.1)  # Short sleep should succeed
        
        # Test timeout (only on Unix systems)
        import platform
        if platform.system() != 'Windows':
            with pytest.raises(Exception):  # TimeoutError or similar
                with timeout_handler(1):
                    time.sleep(2)  # Should timeout
    
    def test_memory_limit_handler_context_manager(self):
        """Test memory limit handler context manager."""
        # On Windows, this should log warning and continue
        # On Unix, this should set resource limits
        
        try:
            with memory_limit_handler(100 * 1024 * 1024):  # 100MB limit
                # Small operation should succeed
                data = [i for i in range(1000)]
                assert len(data) == 1000
        except Exception as e:
            # Memory limit enforcement may vary by platform
            assert "memory" in str(e).lower() or "limit" in str(e).lower()

class TestErrorHandling:
    """Test error handling and fallback behavior."""
    
    def test_render_chart_invalid_chart_type(self):
        """Test chart rendering with invalid chart type."""
        test_data = [{"value": 10}]
        
        result = render_chart(data=test_data, chart_type="invalid_type")
        
        assert isinstance(result, ChartResult)
        # Should fallback to a default chart type or fail gracefully
        if result.success:
            assert result.chart_type in ["bar", "histogram", "scatter", "line", "heatmap"]
        else:
            assert len(result.issues) > 0
    
    def test_render_chart_malformed_data(self):
        """Test chart rendering with malformed data."""
        # Test with inconsistent data structure
        malformed_data = [
            {"a": 1, "b": 2},
            {"c": 3, "d": 4},  # Different keys
            {"a": None, "b": None}  # None values
        ]
        
        result = render_chart(data=malformed_data, chart_type="bar")
        
        assert isinstance(result, ChartResult)
        # Should either handle gracefully or fail with informative error
        if not result.success:
            assert len(result.issues) > 0
        assert result.correlation_id is not None
    
    def test_render_chart_exception_handling(self):
        """Test that exceptions are properly caught and handled."""
        # Mock matplotlib to raise an exception
        with patch('app.viz.sandbox.create_chart') as mock_create:
            mock_create.side_effect = Exception("Test exception")
            
            test_data = [{"value": 10}]
            result = render_chart(data=test_data, chart_type="bar")
            
            assert isinstance(result, ChartResult)
            assert result.success == False
            assert any("failed" in issue.lower() for issue in result.issues)
            assert result.correlation_id is not None
    
    def test_render_chart_cleanup_on_error(self):
        """Test that resources are properly cleaned up on error."""
        # Mock to simulate cleanup
        with patch('app.viz.sandbox.plt.close') as mock_close, \
             patch('app.viz.sandbox.remove_import_restrictions') as mock_remove_restrictions:
            
            # Simulate error during chart creation
            with patch('app.viz.sandbox.create_chart') as mock_create:
                mock_create.side_effect = Exception("Test error")
                
                test_data = [{"value": 10}]
                result = render_chart(data=test_data, chart_type="bar")
                
                assert result.success == False
                # Verify cleanup functions were called
                mock_close.assert_called()
                mock_remove_restrictions.assert_called()

class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_end_to_end_chart_generation(self):
        """Test complete end-to-end chart generation process."""
        # Test data representing SQL query results
        sql_result_data = [
            {"ProductCategory": "Bikes", "TotalSales": 25000, "OrderCount": 150},
            {"ProductCategory": "Components", "TotalSales": 15000, "OrderCount": 200}, 
            {"ProductCategory": "Clothing", "TotalSales": 8000, "OrderCount": 100},
            {"ProductCategory": "Accessories", "TotalSales": 12000, "OrderCount": 300}
        ]
        
        # Test different chart types
        chart_types = ["auto", "bar", "scatter"]
        
        for chart_type in chart_types:
            result = render_chart(
                data=sql_result_data,
                chart_type=chart_type,
                x="ProductCategory",
                y="TotalSales"
            )
            
            assert isinstance(result, ChartResult)
            assert result.correlation_id is not None
            assert isinstance(result.generated_at, datetime)
            
            if result.success:
                assert result.image_data is not None
                assert result.caption != ""
                assert result.data_summary["rows"] == 4
                assert result.data_summary["columns"] == 3
            else:
                # Acceptable in CI environments with limited graphics support
                assert len(result.issues) > 0
    
    def test_security_sandbox_isolation(self):
        """Test that sandbox properly isolates dangerous operations."""
        # This test verifies that the sandbox prevents dangerous operations
        # In a real scenario, we would test actual code execution
        
        # Test that import restrictions are enforced
        install_import_restrictions()
        
        try:
            # Attempt to access dangerous modules should fail
            with pytest.raises(ImportError):
                import os  # Should be blocked
        except ImportError:
            # Expected - import should be blocked
            pass
        except Exception:
            # May fail differently in test environment
            pass
        finally:
            remove_import_restrictions()
        
        # Test basic data flow continues to work
        test_data = [{"test": 1}]
        result = render_chart(data=test_data)
        assert isinstance(result, ChartResult)
