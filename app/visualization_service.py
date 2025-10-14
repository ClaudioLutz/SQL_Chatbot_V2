"""
Visualization service for SQL Chatbot V2.

Provides column type detection, data sampling, and validation
for generating interactive Plotly visualizations.
"""

from typing import Dict, List, Optional, Literal
import pandas as pd
import numpy as np
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Type aliases
ChartType = Literal["scatter", "bar", "line", "histogram"]
ColumnType = Literal["numeric", "categorical", "datetime"]


class VisualizationRequest(BaseModel):
    """Request model for visualization endpoint."""
    columns: List[str]
    rows: List[dict]
    chartType: ChartType
    xColumn: str
    yColumn: Optional[str] = None  # None for histogram
    maxRows: Optional[int] = 10000  # Maximum rows to sample
    bins: Optional[int] = None  # Number of bins for histogram (None = auto)


class CheckVisualizationRequest(BaseModel):
    """Request model for checking visualization availability."""
    columns: List[str]
    rows: List[dict]


# Chart type compatibility matrix
CHART_COMPATIBILITY = {
    "scatter": {"x": ["numeric"], "y": ["numeric"]},
    "bar": {"x": ["categorical"], "y": ["numeric"]},
    "line": {"x": ["datetime", "numeric"], "y": ["numeric"]},
    "histogram": {"x": ["numeric"]},
    "correlation": {"columns": ["numeric"]}  # Multi-select numeric only
}


def check_visualization_availability(columns: List[str], rows: List[dict]) -> dict:
    """
    Check if dataset is suitable for visualization.
    
    Args:
        columns: List of column names
        rows: List of row dictionaries
        
    Returns:
        Dictionary with availability status, column types, and row count
    """
    try:
        # Check minimum rows
        if len(rows) < 2:
            return {
                "available": False,
                "reason": "At least 2 rows required for visualization."
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(rows)
        
        # Detect column types
        column_types = detect_column_types(df)
        
        # Check for at least one numeric column
        has_numeric = any(t == "numeric" for t in column_types.values())
        if not has_numeric:
            return {
                "available": False,
                "reason": "No numeric columns found. Visualizations require at least one numeric column."
            }
        
        return {
            "available": True,
            "column_types": column_types,
            "row_count": len(rows)
        }
        
    except Exception as e:
        logger.error(f"Error checking visualization availability: {str(e)}", exc_info=True)
        return {
            "available": False,
            "reason": "Error checking visualization availability."
        }


def detect_column_types(df: pd.DataFrame) -> Dict[str, ColumnType]:
    """
    Detect column types for visualization compatibility.
    
    Analyzes first 100 non-null values to determine if column is:
    - numeric: Can be converted to numeric type
    - datetime: Matches datetime patterns
    - categorical: Everything else
    
    Special case: Numeric columns with low cardinality (≤10 unique values
    and <5% of total rows) are treated as categorical.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Dictionary mapping column names to types
    """
    column_types = {}
    
    for col in df.columns:
        # Get sample of non-null values
        sample = df[col].dropna().head(100)
        
        if len(sample) == 0:
            # All null column - treat as categorical
            column_types[col] = "categorical"
            continue
        
        # Test 1: Is numeric?
        try:
            pd.to_numeric(sample, errors='raise')
            
            # Check cardinality for categorical override
            unique_count = df[col].nunique()
            total_count = len(df)
            
            if unique_count <= 10 and unique_count < total_count * 0.05:
                # Low cardinality numeric treated as categorical
                column_types[col] = "categorical"
            else:
                column_types[col] = "numeric"
            continue
            
        except (ValueError, TypeError):
            pass
        
        # Test 2: Is datetime?
        try:
            pd.to_datetime(sample, errors='raise')
            column_types[col] = "datetime"
            continue
        except (ValueError, TypeError):
            pass
        
        # Default: categorical
        column_types[col] = "categorical"
    
    return column_types


def validate_chart_compatibility(
    chart_type: ChartType,
    x_column: str,
    y_column: Optional[str],
    column_types: Dict[str, ColumnType]
) -> None:
    """
    Validate that selected columns are compatible with chart type.
    
    Args:
        chart_type: Type of chart to generate
        x_column: Name of X-axis column
        y_column: Name of Y-axis column (None for histogram)
        column_types: Dictionary of column types
        
    Raises:
        ValueError: If column types are incompatible with chart type
    """
    required = CHART_COMPATIBILITY[chart_type]
    
    # Validate X-axis
    if x_column not in column_types:
        raise ValueError(f"Column '{x_column}' not found in dataset.")
    
    if column_types[x_column] not in required["x"]:
        raise ValueError(
            f"X-axis column '{x_column}' (type: {column_types[x_column]}) "
            f"is not compatible with {chart_type} chart. "
            f"Required types: {', '.join(required['x'])}"
        )
    
    # Validate Y-axis (if required)
    if "y" in required and y_column:
        if y_column not in column_types:
            raise ValueError(f"Column '{y_column}' not found in dataset.")
        
        if column_types[y_column] not in required["y"]:
            raise ValueError(
                f"Y-axis column '{y_column}' (type: {column_types[y_column]}) "
                f"is not compatible with {chart_type} chart. "
                f"Required types: {', '.join(required['y'])}"
            )


def sample_large_dataset(df: pd.DataFrame, x_column: str, max_rows: int = 10000) -> dict:
    """
    Sample large datasets while preserving statistical distribution.
    
    Uses stratified sampling for categorical X-axis, systematic sampling for numeric.
    
    Args:
        df: pandas DataFrame to sample
        x_column: Name of X-axis column for stratified sampling
        max_rows: Maximum number of rows to return
        
    Returns:
        Dictionary with sampled data and sampling metadata
    """
    if len(df) <= max_rows:
        return {
            "data": df,
            "sampled": False,
            "original_count": len(df),
            "sampled_count": len(df)
        }
    
    try:
        # Check if X-axis is categorical for stratified sampling
        if df[x_column].dtype == 'object' or df[x_column].dtype.name == 'category':
            # Stratified sampling - preserve distribution across categories
            unique_values = df[x_column].nunique()
            samples_per_category = max(1, max_rows // unique_values)
            
            sampled = df.groupby(x_column, group_keys=False).apply(
                lambda x: x.sample(min(len(x), samples_per_category), random_state=42)
            ).reset_index(drop=True)
            
            # If still too large, do random sampling
            if len(sampled) > max_rows:
                sampled = sampled.sample(n=max_rows, random_state=42)
        else:
            # Systematic sampling for numeric - preserves order/trends
            step = len(df) // max_rows
            indices = np.arange(0, len(df), step)[:max_rows]
            sampled = df.iloc[indices].reset_index(drop=True)
        
        return {
            "data": sampled,
            "sampled": True,
            "original_count": len(df),
            "sampled_count": len(sampled)
        }
        
    except Exception as e:
        logger.warning(f"Error during sampling, falling back to random: {str(e)}")
        # Fallback to random sampling
        sampled = df.sample(n=min(len(df), max_rows), random_state=42)
        return {
            "data": sampled,
            "sampled": True,
            "original_count": len(df),
            "sampled_count": len(sampled)
        }


def prepare_visualization_data(
    df: pd.DataFrame,
    chart_type: ChartType,
    x_column: str,
    y_column: Optional[str],
    max_rows: int = 10000
) -> dict:
    """
    Prepare data for visualization with sampling if needed.
    
    Args:
        df: pandas DataFrame with query results
        chart_type: Type of chart to generate
        x_column: Name of X-axis column
        y_column: Name of Y-axis column (None for histogram)
        max_rows: Maximum rows before sampling
        
    Returns:
        Dictionary with prepared data and metadata
        
    Raises:
        ValueError: If columns are incompatible with chart type
    """
    original_count = len(df)
    
    # Detect column types
    column_types = detect_column_types(df)
    
    # Validate compatibility
    validate_chart_compatibility(chart_type, x_column, y_column, column_types)
    
    # Sample if needed
    sample_result = sample_large_dataset(df, x_column, max_rows)
    df_sampled = sample_result["data"]
    
    # Prepare column list
    columns_to_include = [x_column]
    if y_column:
        columns_to_include.append(y_column)
    
    # Convert to records (filter nulls for cleaner visualization)
    df_filtered = df_sampled[columns_to_include].dropna()
    
    return {
        "status": "success",
        "data": {
            "columns": columns_to_include,
            "rows": df_filtered.to_dict('records')
        },
        "is_sampled": sample_result["sampled"],
        "original_row_count": original_count,
        "sampled_row_count": len(df_sampled) if sample_result["sampled"] else None,
        "column_types": column_types
    }


def validate_correlation_request(
    df: pd.DataFrame,
    columns: List[str]
) -> Dict[str, bool | str]:
    """
    Validate correlation matrix request.
    
    Args:
        df: Input DataFrame
        columns: List of column names to correlate
    
    Returns:
        Dictionary with validation result and error message if invalid
    """
    # Check minimum columns
    if len(columns) < 2:
        return {
            "valid": False,
            "message": "At least 2 columns required for correlation matrix."
        }
    
    # Check maximum columns
    if len(columns) > 15:
        return {
            "valid": False,
            "message": "Maximum 15 columns allowed for correlation matrix."
        }
    
    # Check columns exist
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        return {
            "valid": False,
            "message": f"Columns not found: {', '.join(missing_columns)}"
        }
    
    # Check all columns are numeric
    non_numeric = []
    for col in columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            non_numeric.append(col)
    
    if non_numeric:
        return {
            "valid": False,
            "message": f"Non-numeric columns: {', '.join(non_numeric)}. "
                      f"Correlation matrix requires numeric columns only."
        }
    
    return {"valid": True}


def calculate_correlation_matrix(
    df: pd.DataFrame,
    columns: List[str],
    max_rows: int = 10000
) -> dict:
    """
    Calculate Pearson correlation matrix for selected numeric columns.
    
    Args:
        df: Input DataFrame
        columns: List of column names to correlate (2-15)
        max_rows: Maximum rows before sampling (default 10000)
    
    Returns:
        Dictionary with:
        - status: "success" | "error"
        - correlation_matrix: Dict[str, Dict[str, float]]
        - columns: List[str]
        - is_sampled: bool
        - sample_size: int
        - original_size: int
        - rows_with_missing_data: int
    
    Raises:
        ValueError: For validation errors or insufficient data
    """
    original_count = len(df)
    
    # Sample if needed
    if original_count > max_rows:
        sample_result = sample_large_dataset(df, columns[0], max_rows)
        df_sampled = sample_result["data"]
        is_sampled = True
    else:
        df_sampled = df
        is_sampled = False
    
    # Filter to selected columns and ensure numeric
    df_filtered = df_sampled[columns].select_dtypes(include=[np.number])
    
    # Validate all columns are numeric
    if len(df_filtered.columns) != len(columns):
        non_numeric = set(columns) - set(df_filtered.columns)
        raise ValueError(
            f"Non-numeric columns detected: {', '.join(non_numeric)}. "
            f"Correlation matrix requires numeric columns only."
        )
    
    # Drop rows with any NaN
    df_clean = df_filtered.dropna()
    
    if len(df_clean) < 2:
        raise ValueError(
            "Insufficient data after removing missing values. "
            "At least 2 complete rows required."
        )
    
    # Calculate correlation matrix
    corr_matrix = df_clean.corr()
    
    # Convert to nested dict
    corr_dict = {}
    for col1 in columns:
        corr_dict[col1] = {}
        for col2 in columns:
            corr_dict[col1][col2] = float(corr_matrix.loc[col1, col2])
    
    return {
        "status": "success",
        "correlation_matrix": corr_dict,
        "columns": columns,
        "is_sampled": is_sampled,
        "sample_size": len(df_clean),
        "original_size": original_count,
        "rows_with_missing_data": original_count - len(df_clean)
    }
