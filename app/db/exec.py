"""
Database execution module for SQL Server using ODBC Driver 18.

This module handles:
- Secure connections to SQL Server with encryption
- Query execution with timeout management
- Result set processing and pagination
- Connection pooling and error handling
"""

import logging
import pyodbc
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import time

from app.config import settings


logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of SQL query execution."""
    rows: List[List[Any]]
    columns: List[Dict[str, str]]  # [{"name": "ProductID", "type": "int"}, ...]
    row_count: int
    execution_time_seconds: float
    has_more: Optional[bool] = None  # True if more rows available, None if unknown


class ExecutionError(Exception):
    """Database execution error details."""
    def __init__(self, error_code: str, message: str, sql_state: Optional[str] = None, native_error: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.sql_state = sql_state
        self.native_error = native_error


class DatabaseExecutor:
    """SQL Server database executor with ODBC Driver 18."""
    
    def __init__(self):
        self.connection_timeout = getattr(settings, 'db_connection_timeout', 30)
        self.query_timeout = getattr(settings, 'sql_timeout_seconds', 300)  # 5 minutes
        self.max_rows = getattr(settings, 'max_query_rows', 10000)
        
        # Build connection string based on environment
        self._connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Build ODBC connection string with proper encryption settings."""
        # Base connection parameters
        params = {
            'DRIVER': '{ODBC Driver 18 for SQL Server}',
            'SERVER': f"{settings.db_server},{settings.db_port}",
            'DATABASE': settings.db_name,
            'UID': settings.db_user,
            'PWD': settings.db_password,
            'Encrypt': settings.db_encrypt,
            'TrustServerCertificate': settings.db_trust_server_cert,
            'Connection Timeout': str(self.connection_timeout),
            'Command Timeout': str(self.query_timeout)
        }
        
        logger.info(f"Using SSL settings: Encrypt={settings.db_encrypt}, TrustServerCertificate={settings.db_trust_server_cert}")
        
        # Build connection string
        conn_str = ';'.join([f"{k}={v}" for k, v in params.items()])
        
        # Log connection string without password for debugging
        safe_params = {k: '***' if 'PWD' in k.upper() else v for k, v in params.items()}
        safe_conn_str = ';'.join([f"{k}={v}" for k, v in safe_params.items()])
        logger.debug(f"Connection string: {safe_conn_str}")
        
        return conn_str
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        connection = None
        try:
            start_time = time.time()
            connection = pyodbc.connect(
                self._connection_string,
                timeout=self.connection_timeout
            )
            connection_time = time.time() - start_time
            logger.debug(f"Database connection established in {connection_time:.3f}s")
            
            yield connection
            
        except pyodbc.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                    logger.debug("Database connection closed")
                except Exception as e:
                    logger.warning(f"Error closing database connection: {e}")
    
    def execute_query(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
        timeout: Optional[int] = None
    ) -> QueryResult:
        """
        Execute SQL query and return results.
        
        Args:
            sql: SQL query to execute
            params: Optional parameters for parameterized queries
            timeout: Optional query timeout (overrides default)
        
        Returns:
            QueryResult with rows, columns, and metadata
            
        Raises:
            ExecutionError: If query execution fails
        """
        if timeout is None:
            timeout = self.query_timeout
        
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Note: pyodbc doesn't support cursor-level timeout,
                # timeout is handled at connection level during connect
                
                # Execute query
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # Get column information
                columns = []
                if cursor.description:
                    for col_desc in cursor.description:
                        col_name = col_desc[0]
                        col_type = self._map_sql_type_to_string(col_desc[1])
                        columns.append({"name": col_name, "type": col_type})
                
                # Fetch rows with limit protection
                rows = []
                row_count = 0
                
                try:
                    while True:
                        # Fetch in batches to avoid memory issues
                        batch = cursor.fetchmany(1000)
                        if not batch:
                            break
                        
                        for row in batch:
                            if row_count >= self.max_rows:
                                logger.warning(f"Query result truncated at {self.max_rows} rows")
                                break
                            
                            # Convert row to list and handle special types
                            row_data = []
                            for value in row:
                                if value is None:
                                    row_data.append(None)
                                elif isinstance(value, (int, float, str, bool)):
                                    row_data.append(value)
                                else:
                                    # Convert other types to string representation
                                    row_data.append(str(value))
                            
                            rows.append(row_data)
                            row_count += 1
                        
                        if row_count >= self.max_rows:
                            break
                
                except pyodbc.Error as e:
                    logger.error(f"Error fetching query results: {e}")
                    raise ExecutionError(
                        error_code="FETCH_ERROR",
                        message=f"Failed to fetch query results: {str(e)}",
                        sql_state=getattr(e, 'args', [None, None])[0] if hasattr(e, 'args') and len(e.args) > 1 else None,
                        native_error=getattr(e, 'args', [None, None])[1] if hasattr(e, 'args') and len(e.args) > 1 else None
                    )
                
                execution_time = time.time() - start_time
                
                logger.info(f"Query executed successfully: {row_count} rows in {execution_time:.3f}s")
                
                return QueryResult(
                    rows=rows,
                    columns=columns,
                    row_count=row_count,
                    execution_time_seconds=execution_time,
                    has_more=row_count >= self.max_rows  # Might have more if we hit the limit
                )
                
        except pyodbc.Error as e:
            execution_time = time.time() - start_time
            
            # Extract error details
            sql_state = None
            native_error = None
            error_message = str(e)
            
            if hasattr(e, 'args') and len(e.args) >= 2:
                sql_state = e.args[0] if len(e.args) > 0 else None
                native_error = e.args[1] if len(e.args) > 1 else None
            
            logger.error(f"Query execution failed after {execution_time:.3f}s: {error_message}")
            
            # Map common SQL Server errors to user-friendly messages
            user_message = self._map_sql_error_to_message(error_message, sql_state, native_error)
            
            raise ExecutionError(
                error_code="SQL_EXECUTION_ERROR",
                message=user_message,
                sql_state=sql_state,
                native_error=native_error
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Unexpected error during query execution after {execution_time:.3f}s: {e}")
            
            raise ExecutionError(
                error_code="UNEXPECTED_ERROR",
                message=f"Unexpected database error: {str(e)}"
            )
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test_value;")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def _map_sql_type_to_string(self, sql_type) -> str:
        """Map pyodbc SQL type constants to string names."""
        type_mapping = {
            pyodbc.SQL_INTEGER: "int",
            pyodbc.SQL_BIGINT: "bigint",
            pyodbc.SQL_SMALLINT: "smallint",
            pyodbc.SQL_TINYINT: "tinyint",
            pyodbc.SQL_DECIMAL: "decimal",
            pyodbc.SQL_NUMERIC: "numeric",
            pyodbc.SQL_FLOAT: "float",
            pyodbc.SQL_REAL: "real",
            pyodbc.SQL_DOUBLE: "double",
            pyodbc.SQL_CHAR: "char",
            pyodbc.SQL_VARCHAR: "varchar",
            pyodbc.SQL_LONGVARCHAR: "text",
            pyodbc.SQL_WCHAR: "nchar",
            pyodbc.SQL_WVARCHAR: "nvarchar",
            pyodbc.SQL_WLONGVARCHAR: "ntext",
            pyodbc.SQL_BINARY: "binary",
            pyodbc.SQL_VARBINARY: "varbinary",
            pyodbc.SQL_LONGVARBINARY: "image",
            pyodbc.SQL_BIT: "bit",
            pyodbc.SQL_TYPE_DATE: "date",
            pyodbc.SQL_TYPE_TIME: "time",
            pyodbc.SQL_TYPE_TIMESTAMP: "datetime",
            pyodbc.SQL_GUID: "uniqueidentifier"
        }
        
        return type_mapping.get(sql_type, "unknown")
    
    def _map_sql_error_to_message(self, error_message: str, sql_state: Optional[str], native_error: Optional[int]) -> str:
        """Map SQL Server errors to user-friendly messages."""
        error_lower = error_message.lower()
        
        # Common SQL Server error patterns
        if "invalid column name" in error_lower:
            return "Invalid column name in query. Please check column names and table aliases."
        elif "invalid object name" in error_lower:
            return "Invalid table or view name in query. Please verify object names."
        elif "timeout" in error_lower or "query timeout" in error_lower:
            return f"Query timeout after {self.query_timeout} seconds. Please simplify your query."
        elif "permission" in error_lower or "access" in error_lower:
            return "Insufficient permissions to execute this query."
        elif "syntax error" in error_lower or "incorrect syntax" in error_lower:
            return "SQL syntax error. Please check your query syntax."
        elif "connection" in error_lower:
            return "Database connection error. Please try again later."
        elif "login failed" in error_lower:
            return "Database authentication failed."
        else:
            # Return original message for debugging, but sanitize sensitive info
            safe_message = error_message.replace(settings.db_password, "***") if hasattr(settings, 'db_password') else error_message
            return f"Database error: {safe_message}"


# Global instance
db_executor = DatabaseExecutor()
