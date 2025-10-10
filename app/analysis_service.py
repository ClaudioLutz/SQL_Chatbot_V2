"""
Analysis service for generating statistical summaries using skimpy.
"""
import logging
from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from skimpy import skim

logger = logging.getLogger(__name__)

# Constants
MIN_ROWS = 2
MIN_COLUMNS = 1


def analyze_query_results(columns: List[str], rows: List[Dict]) -> Dict[str, Any]:
    """
    Generate statistical analysis for query results.
    
    Args:
        columns: List of column names
        rows: List of row dictionaries
        
    Returns:
        Dict with status and analysis data or error info
    """
    logger.info(f"Starting analysis: {len(rows)} rows, {len(columns)} columns")
    
    # Validation
    is_valid, error_code = _validate_dataset_requirements(columns, rows)
    if not is_valid:
        # error_code is guaranteed to be a string when is_valid is False
        assert error_code is not None
        return _create_error_response(error_code, len(rows), len(columns))
    
    try:
        # Convert to DataFrame
        df = _convert_to_dataframe(columns, rows)
        
        # Generate skimpy analysis
        skim_result = skim(df)
        
        # Extract structured data
        analysis = {
            "status": "success",
            "row_count": len(rows),
            "column_count": len(columns),
            "variable_types": _extract_variable_types(df),
            "numeric_stats": _extract_numeric_stats(df),
            "cardinality": _extract_cardinality(df),
            "missing_values": _extract_missing_values(df)
        }
        
        logger.info("Analysis completed successfully")
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Analysis could not be generated for this dataset.",
            "error_detail": str(e)
        }


def _validate_dataset_requirements(
    columns: List[str], 
    rows: List[Dict]
) -> Tuple[bool, Optional[str]]:
    """
    Validate minimum dataset requirements.
    
    Returns:
        (is_valid, error_code)
    """
    if len(columns) < MIN_COLUMNS:
        return False, "no_columns"
    
    if len(rows) < MIN_ROWS:
        return False, "insufficient_rows"
    
    return True, None


def _create_error_response(
    error_code: str, 
    row_count: int, 
    column_count: int
) -> Dict[str, Any]:
    """Create appropriate error response based on error code."""
    messages = {
        "no_columns": "No columns to analyze.",
        "insufficient_rows": "Analysis requires at least 2 rows of data."
    }
    
    response = {
        "status": error_code,
        "row_count": row_count,
        "column_count": column_count,
        "message": messages.get(error_code, "Unknown error")
    }
    
    return response


def _convert_to_dataframe(columns: List[str], rows: List[Dict]) -> pd.DataFrame:
    """Convert API data format to pandas DataFrame."""
    return pd.DataFrame(rows, columns=columns)


def _extract_variable_types(df: pd.DataFrame) -> Dict[str, int]:
    """Extract column type distribution."""
    type_counts = {
        "numeric": 0,
        "categorical": 0,
        "datetime": 0,
        "other": 0
    }
    
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            type_counts["numeric"] += 1
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            type_counts["datetime"] += 1
        elif pd.api.types.is_object_dtype(dtype) or str(dtype) == 'category':
            type_counts["categorical"] += 1
        else:
            type_counts["other"] += 1
    
    return type_counts


def _extract_numeric_stats(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract numeric column statistics."""
    stats = []
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    for col in numeric_cols:
        col_stats = {
            "column": col,
            "count": int(df[col].count()),
            "mean": float(df[col].mean()) if not df[col].isna().all() else None,
            "std": float(df[col].std()) if not df[col].isna().all() else None,
            "min": float(df[col].min()) if not df[col].isna().all() else None,
            "q25": float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
            "q50": float(df[col].quantile(0.50)) if not df[col].isna().all() else None,
            "q75": float(df[col].quantile(0.75)) if not df[col].isna().all() else None,
            "max": float(df[col].max()) if not df[col].isna().all() else None
        }
        stats.append(col_stats)
    
    return stats


def _extract_cardinality(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract unique value counts for each column."""
    cardinality = []
    
    for col in df.columns:
        cardinality.append({
            "column": col,
            "unique_count": int(df[col].nunique()),
            "total_count": len(df)
        })
    
    return cardinality


def _extract_missing_values(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract null/missing value analysis."""
    missing = []
    
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        total_count = len(df)
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
        
        missing.append({
            "column": col,
            "null_count": null_count,
            "null_percentage": round(null_percentage, 2)
        })
    
    return missing
