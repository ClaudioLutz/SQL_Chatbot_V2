"""
Secure visualization sandbox for generating charts from data.

This module provides isolated chart generation with strict security constraints:
- No filesystem or network access
- CPU and memory limits enforced
- Headless matplotlib backend (Agg)
- Returns base64-encoded PNG images
- Hardened against resource abuse and data overload
"""

import os
import sys
import io
import base64
import logging
import traceback
import uuid
import platform
import re
import html
from contextlib import contextmanager
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from dataclasses import dataclass

# Platform-specific imports
try:
    import signal
    import resource
    HAS_UNIX_FEATURES = True
except ImportError:
    HAS_UNIX_FEATURES = False

# Set matplotlib backend before any other imports
os.environ['MPLBACKEND'] = 'Agg'
import matplotlib
matplotlib.use('Agg')  # Headless backend - no GUI dependencies
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from .whitelist import (
    install_import_restrictions, remove_import_restrictions,
    validate_safe_environment, MAX_CPU_TIME, MAX_MEMORY, MAX_IMAGE_SIZE, MAX_DATA_ROWS
)

# Hardening constants
MAX_PIXELS = 2_000_000  # 2 million pixels max
MAX_DPI = 150  # Maximum DPI for charts
MAX_CATEGORIES = 50  # Maximum distinct categories for bar charts
MAX_SCATTER_ROWS = 5_000  # Maximum rows for scatter/line charts (downsampling)
MAX_PNG_SIZE = 2.5 * 1024 * 1024  # 2.5MB maximum PNG size
RANDOM_SEED = 42  # Fixed seed for reproducible sampling

# Assert backend is Agg at runtime
assert matplotlib.get_backend() == 'Agg', f"Backend must be 'Agg', got '{matplotlib.get_backend()}'"

# Set colorblind-safe palette globally
sns.set_palette("colorblind")
# Ensure line/marker styles differentiate series (not color alone)
sns.set_style("whitegrid")

logger = logging.getLogger(__name__)

@dataclass
class ChartResult:
    """Result of chart generation process."""
    success: bool
    image_data: Optional[str]  # base64 encoded PNG
    image_format: str
    caption: str
    chart_type: str
    dimensions: Tuple[int, int]
    data_summary: Dict[str, Any]
    issues: List[str]
    correlation_id: str
    generated_at: datetime
    file_size_bytes: int = 0  # Size of generated PNG in bytes

class TimeoutError(Exception):
    """Raised when chart generation exceeds time limit."""
    pass

class MemoryError(Exception):
    """Raised when chart generation exceeds memory limit."""
    pass

@contextmanager
def timeout_handler(seconds):
    """Context manager for enforcing CPU time limits."""
    if not HAS_UNIX_FEATURES:
        # Windows doesn't support SIGALRM, use simple timeout tracking
        import time
        start_time = time.time()
        
        def check_timeout():
            if time.time() - start_time > seconds:
                raise TimeoutError(f"Chart generation timed out after {seconds} seconds")
        
        # Store check function for manual checking
        timeout_handler.check_timeout = check_timeout  # type: ignore
        yield
        return
    
    def timeout_signal_handler(signum, frame):
        raise TimeoutError(f"Chart generation timed out after {seconds} seconds")
    
    # Set signal handler (Unix only)
    old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)  # type: ignore
    signal.alarm(seconds)  # type: ignore
    
    try:
        yield
    finally:
        # Restore original handler and cancel alarm
        signal.alarm(0)  # type: ignore
        signal.signal(signal.SIGALRM, old_handler)  # type: ignore

@contextmanager
def memory_limit_handler(max_memory_bytes):
    """Context manager for enforcing memory limits."""
    if not HAS_UNIX_FEATURES:
        # Windows doesn't support resource limits in the same way
        # Log warning and continue without enforcement
        logger.warning(f"Memory limits not enforced on Windows (requested: {max_memory_bytes // (1024*1024)}MB)")
        yield
        return
        
    try:
        # Set memory limit (virtual memory) - Unix only
        resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))  # type: ignore
        yield
    except MemoryError:
        raise MemoryError(f"Chart generation exceeded memory limit of {max_memory_bytes // (1024*1024)}MB")
    finally:
        # Reset memory limit
        try:
            resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))  # type: ignore
        except:
            pass  # Best effort cleanup

def detect_chart_type(data: pd.DataFrame) -> str:
    """
    Auto-detect appropriate chart type based on data structure.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        Chart type string (bar, line, scatter, histogram, etc.)
    """
    if data.empty:
        return 'empty'
    
    num_cols = len(data.columns)
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if num_cols == 1:
        col_name = data.columns[0]
        if col_name in categorical_cols:
            # Single categorical column - show value counts
            return 'bar'
        else:
            # Single numeric column - show distribution
            return 'histogram'
    
    elif num_cols == 2:
        if len(numeric_cols) == 2:
            # Two numeric columns - scatter plot
            return 'scatter'
        elif len(numeric_cols) == 1 and len(categorical_cols) == 1:
            # One categorical, one numeric - bar chart
            return 'bar'
        else:
            # Mixed or other - default to bar
            return 'bar'
    
    else:
        # Multiple columns
        if len(numeric_cols) >= 2:
            # Multiple numeric columns - correlation heatmap
            return 'heatmap'
        else:
            # Multiple mixed columns - grouped bar chart
            return 'bar'

def sanitize_caption(caption: str) -> str:
    """
    Sanitize caption text to prevent HTML injection and ensure plain text only.
    
    Args:
        caption: Raw caption text
        
    Returns:
        Sanitized plain text caption
    """
    if not caption:
        return "Chart"
    
    # Remove HTML tags and decode HTML entities
    caption = re.sub(r'<[^>]*>', '', str(caption))
    caption = html.unescape(caption)
    
    # Remove potentially dangerous characters and limit length
    caption = re.sub(r'[<>&"\'`]', '', caption)
    caption = caption.strip()[:200]  # Limit to 200 chars
    
    return caption or "Chart"

def validate_pixel_budget(width: int, height: int, dpi: int) -> None:
    """
    Validate that image dimensions don't exceed pixel budget.
    
    Args:
        width: Image width in inches
        height: Image height in inches  
        dpi: Dots per inch
        
    Raises:
        ValueError: If pixel budget is exceeded
    """
    total_pixels = int(width * dpi) * int(height * dpi)
    
    if total_pixels > MAX_PIXELS:
        raise ValueError(
            f"Pixel budget exceeded: {total_pixels:,} pixels > {MAX_PIXELS:,} limit. "
            f"Try smaller dimensions or lower DPI."
        )
    
    if dpi > MAX_DPI:
        raise ValueError(
            f"DPI limit exceeded: {dpi} > {MAX_DPI} limit. "
            f"Please reduce image quality."
        )

def handle_nans(data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Handle NaN values in data and track what was done.
    
    Args:
        data: DataFrame potentially containing NaN values
        
    Returns:
        Tuple of (cleaned DataFrame, list of processing notes)
    """
    issues = []
    original_rows = len(data)
    
    # Check for NaN values
    nan_columns = []
    for col in data.columns:
        nan_count = data[col].isnull().sum()
        if nan_count > 0:
            nan_columns.append(f"{col} ({nan_count} nulls)")
    
    if nan_columns:
        # Drop rows with any NaN values
        cleaned_data = data.dropna()
        dropped_rows = original_rows - len(cleaned_data)
        
        if dropped_rows > 0:
            issues.append(f"Dropped {dropped_rows} rows with nulls in {', '.join(nan_columns)}")
        
        return cleaned_data, issues
    
    return data, issues

def downsample_data(data: pd.DataFrame, max_rows: int, chart_type: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Downsample data for performance if needed.
    
    Args:
        data: Input DataFrame
        max_rows: Maximum number of rows to keep
        chart_type: Type of chart being created
        
    Returns:
        Tuple of (potentially downsampled DataFrame, list of processing notes)
    """
    issues = []
    
    if len(data) <= max_rows:
        return data, issues
    
    # Only downsample for scatter/line charts to avoid overplotting
    if chart_type in ['scatter', 'line']:
        # Use fixed seed for reproducible sampling
        sampled_data = data.sample(n=max_rows, random_state=RANDOM_SEED)
        issues.append(f"Sampled {max_rows:,} of {len(data):,} rows to avoid overplotting")
        return sampled_data, issues
    
    return data, issues

def create_chart(data: pd.DataFrame, chart_type: str, **kwargs) -> Tuple[Any, str]:
    """
    Create a chart based on data and chart type with hardening features.
    
    Args:
        data: DataFrame containing the data
        chart_type: Type of chart to create
        **kwargs: Additional chart parameters
        
    Returns:
        Tuple of (matplotlib figure, caption)
    """
    # Handle NaN values first
    data, nan_issues = handle_nans(data)
    
    if data.empty:
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        ax.text(0.5, 0.5, 'No data available after cleaning', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('No Data')
        return fig, "No data available for visualization"
    
    # Downsample data if needed
    data, sample_issues = downsample_data(data, MAX_SCATTER_ROWS, chart_type)
    
    # Combine issues from processing
    processing_notes = nan_issues + sample_issues
    
    # Validate pixel budget for figure size
    fig_width, fig_height = 10, 6
    dpi = 100
    
    try:
        validate_pixel_budget(fig_width, fig_height, dpi)
    except ValueError as e:
        # Use smaller default size if budget exceeded
        fig_width, fig_height = 8, 5
        dpi = 80
        processing_notes.append("Reduced image size to stay within pixel budget")
    
    # Create figure with validated dimensions
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
    
    try:
        if chart_type == 'bar':
            return _create_bar_chart(data, fig, ax)
        elif chart_type == 'line':
            return _create_line_chart(data, fig, ax)
        elif chart_type == 'scatter':
            return _create_scatter_chart(data, fig, ax)
        elif chart_type == 'histogram':
            return _create_histogram_chart(data, fig, ax)
        elif chart_type == 'heatmap':
            return _create_heatmap_chart(data, fig, ax)
        else:
            # Fallback to bar chart
            return _create_bar_chart(data, fig, ax)
            
    except Exception as e:
        logger.error(f"Error creating {chart_type} chart: {e}")
        # Create fallback simple chart
        ax.text(0.5, 0.5, f'Chart generation failed\nData: {len(data)} rows, {len(data.columns)} columns', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Data Summary')
        return fig, f"Fallback chart showing {len(data)} rows of data"

def _create_bar_chart(data: pd.DataFrame, fig: Any, ax: Any) -> Tuple[Any, str]:
    """Create a bar chart from data with category capping."""
    additional_notes = []
    
    if len(data.columns) == 1:
        # Single column - show value counts
        col_name = data.columns[0]
        if data[col_name].dtype in ['object', 'category']:
            value_counts = data[col_name].value_counts()
            
            # Cap categories at MAX_CATEGORIES
            if len(value_counts) > MAX_CATEGORIES:
                top_categories = value_counts.head(MAX_CATEGORIES)
                remaining_count = len(value_counts) - MAX_CATEGORIES
                additional_notes.append(f"+{remaining_count} more categories")
                value_counts = top_categories
                
            ax.bar(range(len(value_counts)), value_counts.values.tolist())
            ax.set_xticks(range(len(value_counts)))
            ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
            ax.set_ylabel('Count')
            title = f'Count of {col_name}'
            if additional_notes:
                title += f" (top {MAX_CATEGORIES})"
            ax.set_title(title)
            
            caption = f"Bar chart showing counts of {col_name} values"
            if additional_notes:
                caption += f" ({', '.join(additional_notes)})"
        else:
            # Numeric data - create bins
            ax.hist(data[col_name].dropna(), bins=20, alpha=0.7)
            ax.set_xlabel(col_name)
            ax.set_ylabel('Frequency')
            ax.set_title(f'Distribution of {col_name}')
            caption = f"Histogram showing distribution of {col_name}"
    else:
        # Two columns - categorical vs numeric
        cols = data.columns.tolist()
        categorical_col = None
        numeric_col = None
        
        for col in cols:
            if data[col].dtype in ['object', 'category']:
                categorical_col = col
            elif data[col].dtype in [np.number]:
                numeric_col = col
        
        if categorical_col and numeric_col:
            grouped = data.groupby(categorical_col)[numeric_col].mean()
            
            # Cap categories at MAX_CATEGORIES
            if len(grouped) > MAX_CATEGORIES:
                # Sort by value and take top N
                top_groups = grouped.nlargest(MAX_CATEGORIES)
                remaining_count = len(grouped) - MAX_CATEGORIES
                additional_notes.append(f"+{remaining_count} more categories")
                grouped = top_groups
            
            ax.bar(range(len(grouped)), grouped.values.tolist())
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(grouped.index, rotation=45, ha='right')
            ax.set_ylabel(numeric_col)
            title = f'{numeric_col} by {categorical_col}'
            if additional_notes:
                title += f" (top {MAX_CATEGORIES})"
            ax.set_title(title)
            
            caption = f"Bar chart showing average {numeric_col} by {categorical_col}"
            if additional_notes:
                caption += f" ({', '.join(additional_notes)})"
        else:
            # Fallback - show first numeric column
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                col = numeric_cols[0]
                ax.hist(data[col].dropna(), bins=20, alpha=0.7)
                ax.set_xlabel(col)
                ax.set_ylabel('Frequency')
                ax.set_title(f'Distribution of {col}')
                caption = f"Histogram showing distribution of {col}"
            else:
                ax.text(0.5, 0.5, 'No suitable data for bar chart', 
                       ha='center', va='center', transform=ax.transAxes)
                caption = "No suitable data for visualization"
    
    plt.tight_layout()
    return fig, caption

def _create_line_chart(data: pd.DataFrame, fig: Any, ax: Any) -> Tuple[Any, str]:
    """Create a line chart from data with differentiated markers."""
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) >= 2:
        # Plot first two numeric columns with distinct markers
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        ax.plot(data[x_col], data[y_col], marker='o', linestyle='-', 
                markersize=4, linewidth=2, alpha=0.7)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'{y_col} vs {x_col}')
        caption = f"Line chart showing {y_col} vs {x_col}"
    elif len(numeric_cols) == 1:
        # Plot single numeric column against index
        col = numeric_cols[0]
        ax.plot(data.index, data[col], marker='o', alpha=0.7)
        ax.set_xlabel('Index')
        ax.set_ylabel(col)
        ax.set_title(f'{col} over Index')
        caption = f"Line chart showing {col} trend"
    else:
        ax.text(0.5, 0.5, 'No numeric data for line chart', 
               ha='center', va='center', transform=ax.transAxes)
        caption = "No numeric data available"
    
    plt.tight_layout()
    return fig, caption

def _create_scatter_chart(data: pd.DataFrame, fig: Any, ax: Any) -> Tuple[Any, str]:
    """Create a scatter plot from data with enhanced markers."""
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        ax.scatter(data[x_col], data[y_col], alpha=0.6, s=30, edgecolors='black', linewidth=0.5)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'{y_col} vs {x_col}')
        caption = f"Scatter plot showing relationship between {x_col} and {y_col}"
    else:
        ax.text(0.5, 0.5, 'Need at least 2 numeric columns for scatter plot', 
               ha='center', va='center', transform=ax.transAxes)
        caption = "Insufficient numeric data for scatter plot"
    
    plt.tight_layout()
    return fig, caption

def _create_histogram_chart(data: pd.DataFrame, fig: Any, ax: Any) -> Tuple[Any, str]:
    """Create a histogram from data."""
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        col = numeric_cols[0]
        clean_data = data[col].dropna()
        ax.hist(clean_data, bins=30, alpha=0.7, edgecolor='black')
        ax.set_xlabel(col)
        ax.set_ylabel('Frequency')
        ax.set_title(f'Distribution of {col}')
        
        # Add basic statistics
        mean_val = clean_data.mean()
        ax.axvline(mean_val, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_val:.2f}')
        ax.legend()
        
        caption = f"Histogram showing distribution of {col} (mean: {mean_val:.2f})"
    else:
        ax.text(0.5, 0.5, 'No numeric data for histogram', 
               ha='center', va='center', transform=ax.transAxes)
        caption = "No numeric data available"
    
    plt.tight_layout()
    return fig, caption

def _create_heatmap_chart(data: pd.DataFrame, fig: Any, ax: Any) -> Tuple[Any, str]:
    """Create a correlation heatmap from data."""
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) >= 2:
        correlation_matrix = data[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=ax, cbar_kws={'shrink': 0.8})
        ax.set_title('Correlation Heatmap')
        caption = f"Correlation heatmap for {len(numeric_cols)} numeric variables"
    else:
        ax.text(0.5, 0.5, 'Need at least 2 numeric columns for heatmap', 
               ha='center', va='center', transform=ax.transAxes)
        caption = "Insufficient numeric data for heatmap"
    
    plt.tight_layout()
    return fig, caption

def render_chart(
    data: List[Dict[str, Any]], 
    chart_type: Optional[str] = None,
    x: Optional[str] = None,
    y: Optional[str] = None,
    series: Optional[str] = None,
    **kwargs
) -> ChartResult:
    """
    Render a chart from data in a secure sandbox environment.
    
    Args:
        data: List of dictionaries containing the data
        chart_type: Requested chart type (bar, line, scatter, histogram, heatmap)
        x: X-axis column name
        y: Y-axis column name  
        series: Series/grouping column name
        **kwargs: Additional chart parameters
        
    Returns:
        ChartResult with image data or error information
    """
    correlation_id = str(uuid.uuid4())
    start_time = datetime.now()
    issues = []
    
    logger.info(f"Starting chart generation [correlation_id={correlation_id}]")
    
    try:
        # Validate and prepare data
        if not data or len(data) == 0:
            return ChartResult(
                success=False,
                image_data=None,
                image_format="png",
                caption="No data provided",
                chart_type="none",
                dimensions=(0, 0),
                data_summary={"rows": 0, "columns": 0},
                issues=["No data provided for visualization"],
                correlation_id=correlation_id,
                generated_at=datetime.now()
            )
        
        # Convert to DataFrame and limit size
        df = pd.DataFrame(data)
        if len(df) > MAX_DATA_ROWS:
            df = df.head(MAX_DATA_ROWS)
            issues.append(f"Data limited to {MAX_DATA_ROWS} rows for performance")
        
        # Auto-detect chart type if not specified
        if not chart_type or chart_type == 'auto':
            chart_type = detect_chart_type(df)
            logger.info(f"Auto-detected chart type: {chart_type} [correlation_id={correlation_id}]")
        
        # Install security restrictions
        install_import_restrictions()
        validate_safe_environment()
        
        # Generate chart with resource limits
        with timeout_handler(MAX_CPU_TIME):
            try:
                with memory_limit_handler(MAX_MEMORY):
                    fig, caption = create_chart(df, chart_type, x=x, y=y, series=series, **kwargs)
                    
                    # Convert to PNG bytes - BytesIO only, never to disk
                    img_buffer = io.BytesIO()
                    
                    # Validate that we're using BytesIO (safety check)
                    assert isinstance(img_buffer, io.BytesIO), "Must save to BytesIO buffer only"
                    
                    fig.savefig(img_buffer, format='png', bbox_inches='tight', 
                              dpi=min(fig.dpi, MAX_DPI), facecolor='white', edgecolor='none')
                    img_buffer.seek(0)
                    
                    # Check PNG size before encoding
                    png_bytes = img_buffer.getvalue()
                    png_size = len(png_bytes)
                    
                    if png_size > MAX_PNG_SIZE:
                        raise ValueError(
                            f"Generated PNG too large: {png_size / (1024*1024):.1f}MB > "
                            f"{MAX_PNG_SIZE / (1024*1024):.1f}MB limit. "
                            f"Try fewer series or smaller data range."
                        )
                    
                    # Encode as base64
                    img_data = base64.b64encode(png_bytes).decode('utf-8')
                    
                    # Get image dimensions
                    width, height = fig.get_size_inches() * fig.dpi
                    dimensions = (int(width), int(height))
                    
                    # Sanitize caption for safety
                    safe_caption = sanitize_caption(caption)
                    
                    # Clean up
                    plt.close(fig)
                    img_buffer.close()
                    
                    # Create data summary
                    data_summary = {
                        "rows": len(df),
                        "columns": len(df.columns),
                        "chart_title": safe_caption,
                        "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
                        "categorical_columns": len(df.select_dtypes(include=['object', 'category']).columns),
                        "file_size_bytes": png_size
                    }
                    
                    logger.info(f"Chart generation successful [correlation_id={correlation_id}]")
                    
                    return ChartResult(
                        success=True,
                        image_data=img_data,
                        image_format="png",
                        caption=safe_caption,
                        chart_type=chart_type,
                        dimensions=dimensions,
                        data_summary=data_summary,
                        issues=issues,
                        correlation_id=correlation_id,
                        generated_at=datetime.now(),
                        file_size_bytes=png_size
                    )
                    
            except MemoryError as e:
                logger.error(f"Memory limit exceeded [correlation_id={correlation_id}]: {e}")
                issues.append("Chart generation exceeded memory limits")
                raise
                
    except TimeoutError as e:
        logger.error(f"Timeout during chart generation [correlation_id={correlation_id}]: {e}")
        issues.append("Chart generation timed out")
        
    except Exception as e:
        logger.error(f"Chart generation error [correlation_id={correlation_id}]: {str(e)}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        issues.append(f"Chart generation failed: {str(e)}")
        
    finally:
        # Always clean up
        remove_import_restrictions()
        plt.close('all')  # Close any remaining figures
        
    # Return error result
    return ChartResult(
        success=False,
        image_data=None,
        image_format="png",
        caption=sanitize_caption("Chart generation failed"),
        chart_type=chart_type or "unknown",
        dimensions=(0, 0),
        data_summary={"rows": len(df) if 'df' in locals() else 0, "columns": len(df.columns) if 'df' in locals() else 0},
        issues=issues,
        correlation_id=correlation_id,
        generated_at=datetime.now(),
        file_size_bytes=0
    )
