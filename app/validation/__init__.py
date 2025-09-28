"""
SQL Validation Module

This module provides SQL validation functionality to ensure only safe,
read-only SELECT operations are permitted against the database.
"""

from .sql_validator import ValidationIssue, ValidationResult, validate_sql

__all__ = ["ValidationIssue", "ValidationResult", "validate_sql"]
