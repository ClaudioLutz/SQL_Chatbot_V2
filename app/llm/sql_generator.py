"""
LLM-powered SQL generation service for converting natural language to T-SQL.

This module handles:
- OpenAI GPT-5 integration for SQL generation
- Schema context building for AdventureWorks database
- Error repair through iterative prompting
- T-SQL dialect enforcement with proper pagination patterns
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import openai
from openai import AsyncOpenAI

from app.config import settings
from app.validation.sql_validator import ValidationResult, validate_sql


logger = logging.getLogger(__name__)


@dataclass
class SqlGenResult:
    """Result of SQL generation process."""
    sql: str
    issues: List[str]
    meta: Dict
    correlation_id: str
    generated_at: datetime


@dataclass
class RepairAttempt:
    """Details of a repair attempt."""
    attempt_number: int
    original_error: str
    repair_prompt: str
    generated_sql: str
    success: bool


class SqlGenerator:
    """T-SQL generator using OpenAI GPT-5 with schema context and error repair."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.max_repair_attempts = 3
        self.request_timeout = 30
        
        # AdventureWorks schema context - key tables and columns
        self.schema_context = {
            "Production.Product": {
                "columns": ["ProductID", "Name", "ProductNumber", "Color", "ListPrice", "StandardCost", "ProductCategoryID", "ProductSubcategoryID"],
                "description": "Products catalog with pricing and categorization",
                "sample_data": ["(1, 'HL Road Frame - Black, 58', 'FR-R92B-58', 'Black', 1431.50, 868.63, 18, 1)"]
            },
            "Production.ProductCategory": {
                "columns": ["ProductCategoryID", "Name", "ModifiedDate"],
                "description": "Product categories (Bikes, Components, Clothing, Accessories)",
                "sample_data": ["(1, 'Bikes', '2008-04-30 00:00:00.000')"]
            },
            "Production.ProductSubcategory": {
                "columns": ["ProductSubcategoryID", "ProductCategoryID", "Name"],
                "description": "Product subcategories like Road Bikes, Mountain Bikes, etc.",
                "sample_data": ["(1, 1, 'Mountain Bikes')"]
            },
            "Sales.Customer": {
                "columns": ["CustomerID", "PersonID", "StoreID", "TerritoryID", "AccountNumber"],
                "description": "Customer records with territory assignments",
                "sample_data": ["(1, NULL, 1, 1, 'AW00000001')"]
            },
            "Sales.SalesOrderHeader": {
                "columns": ["SalesOrderID", "RevisionNumber", "OrderDate", "DueDate", "ShipDate", "Status", "CustomerID", "SalesPersonID", "TerritoryID", "BillToAddressID", "ShipToAddressID", "ShipMethodID", "CreditCardID", "SubTotal", "TaxAmt", "Freight", "TotalDue"],
                "description": "Sales order headers with customer and financial information",
                "sample_data": ["(43659, 8, '2011-05-31', '2011-06-12', '2011-06-07', 5, 29825, 279, 5, 985, 985, 5, 16281, 20565.62, 1971.5149, 616.0984, 23153.2339)"]
            },
            "Sales.SalesOrderDetail": {
                "columns": ["SalesOrderID", "SalesOrderDetailID", "CarrierTrackingNumber", "OrderQty", "ProductID", "SpecialOfferID", "UnitPrice", "UnitPriceDiscount", "LineTotal"],
                "description": "Individual line items for sales orders",
                "sample_data": ["(43659, 1, '4911-403C-98', 1, 776, 1, 2024.994, 0.00, 2024.994)"]
            },
            "Person.Person": {
                "columns": ["BusinessEntityID", "PersonType", "NameStyle", "Title", "FirstName", "MiddleName", "LastName", "Suffix", "EmailPromotion"],
                "description": "Person records for customers and employees",
                "sample_data": ["(1, 'EM', 0, 'Mr.', 'Ken', 'J', 'Sánchez', NULL, 0)"]
            },
            "Person.Address": {
                "columns": ["AddressID", "AddressLine1", "AddressLine2", "City", "StateProvinceID", "PostalCode", "SpatialLocation"],
                "description": "Address information for customers and locations",
                "sample_data": ["(1, '1970 Napa Ct.', NULL, 'Bothell', 79, '98011', NULL)"]
            }
        }
        
        # Error patterns and repair strategies
        self.error_patterns = {
            "Invalid column name": "The column '{column}' doesn't exist. Use only these columns: {available_columns}",
            "Invalid object name": "The table '{table}' doesn't exist. Use only these tables: {available_tables}",
            "ORDER BY items must appear in the select list when SELECT DISTINCT is specified": "When using DISTINCT, include ORDER BY columns in SELECT clause",
            "TOP clause requires an ORDER BY": "Add ORDER BY clause when using TOP for deterministic results",
            "The multi-part identifier": "Column reference '{column}' is ambiguous. Use proper table aliases"
        }
    
    def _build_system_prompt(self, allowed_tables: Optional[List[str]] = None) -> str:
        """Build comprehensive system prompt with schema context."""
        if not allowed_tables:
            allowed_tables = list(self.schema_context.keys())
        
        # Build schema information
        schema_info = []
        for table_name in allowed_tables:
            if table_name in self.schema_context:
                table_info = self.schema_context[table_name]
                schema_info.append(f"""
{table_name}:
  Description: {table_info['description']}
  Columns: {', '.join(table_info['columns'])}
  Example: {table_info['sample_data'][0] if table_info['sample_data'] else 'No sample data'}
""")
        
        schema_context = "\n".join(schema_info)
        allowed_list = ", ".join(allowed_tables)
        
        return f"""You are a T-SQL expert working with Microsoft SQL Server 2022 and the AdventureWorks database.

SCHEMA CONTEXT:
{schema_context}

CRITICAL REQUIREMENTS:
• Use T-SQL dialect ONLY (Microsoft SQL Server 2022)
• For pagination, ALWAYS use: ORDER BY ... OFFSET {{offset}} ROWS FETCH NEXT {{page_size}} ROWS ONLY
• ALWAYS include ORDER BY with a unique tiebreaker (like primary key) for deterministic results
• Use only these allowed tables: {allowed_list}
• NO comments in output SQL
• NO multi-statements (semicolons except final terminator)
• NO dynamic SQL construction
• Prefer INNER JOINs over WHERE clause joins
• Use proper table aliases for clarity

PAGINATION RULES:
• If user asks for "top N" or "first N", use ORDER BY + OFFSET 0 ROWS FETCH NEXT N ROWS ONLY
• If user asks for page-based results, calculate OFFSET = (page - 1) * page_size
• ORDER BY clause is MANDATORY for OFFSET/FETCH - it's part of the ORDER BY syntax
• Include unique column (usually primary key) in ORDER BY to ensure deterministic results

Generate ONLY the T-SQL query, no explanations or comments."""

    def _build_repair_prompt(self, original_query: str, error_message: str, validation_issues: List[str]) -> str:
        """Build repair prompt based on error patterns."""
        repair_constraints = []
        
        # Map validation issues to constraints
        for issue in validation_issues:
            if "ORDER BY" in issue:
                repair_constraints.append("Add ORDER BY clause with unique tiebreaker (primary key)")
            elif "table" in issue.lower() and "not allowed" in issue.lower():
                repair_constraints.append("Use only allowed tables from the schema context")
            elif "column" in issue.lower():
                repair_constraints.append("Use only existing columns from the schema context")
        
        # Map database errors to constraints
        if "Invalid column name" in error_message:
            repair_constraints.append("Fix column name - check schema context for correct column names")
        elif "Invalid object name" in error_message:
            repair_constraints.append("Fix table name - use only allowed tables from schema context")
        elif "ORDER BY" in error_message:
            repair_constraints.append("Add proper ORDER BY clause - required for TOP and OFFSET/FETCH")
        
        constraints_text = "\n• ".join(repair_constraints) if repair_constraints else "Fix the SQL syntax error"
        
        return f"""The previous query had errors. Fix these issues:

ORIGINAL QUERY:
{original_query}

ERROR MESSAGE:
{error_message}

VALIDATION ISSUES:
{validation_issues}

REPAIR CONSTRAINTS:
• {constraints_text}

Generate the corrected T-SQL query following all the original requirements."""

    async def generate_sql(
        self,
        prompt: str,
        page: int = 1,
        page_size: int = 20,
        allowed_tables: Optional[List[str]] = None
    ) -> SqlGenResult:
        """Generate T-SQL from natural language with error repair."""
        correlation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        logger.info(f"Starting SQL generation for prompt: '{prompt[:100]}...' [correlation_id={correlation_id}]")
        
        # Calculate pagination offset
        offset = (page - 1) * page_size
        
        # Build user prompt with pagination context
        user_prompt = f"""USER QUESTION: {prompt}

PAGINATION CONTEXT:
• Return page {page} with {page_size} results per page
• Use OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
• Include ORDER BY with unique tiebreaker for deterministic results

Generate the T-SQL query:"""

        system_prompt = self._build_system_prompt(allowed_tables)
        
        repair_attempts = []
        issues = []
        
        try:
            # Initial generation attempt
            response = await self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 as GPT-5 might not be available yet
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.1,  # Low temperature for deterministic SQL
                timeout=self.request_timeout
            )
            
            generated_sql = response.choices[0].message.content
            if generated_sql is None:
                generated_sql = ""
            else:
                generated_sql = generated_sql.strip()
            
            if not generated_sql:
                return SqlGenResult(
                    sql="",
                    issues=["Empty response from OpenAI API"],
                    meta={
                        "model": "gpt-4",
                        "repair_attempts": 0,
                        "generation_time_seconds": (datetime.now() - start_time).total_seconds(),
                        "validation_passed": False,
                        "error": "empty_response"
                    },
                    correlation_id=correlation_id,
                    generated_at=datetime.now()
                )
            
            # Clean up the SQL (remove code block markers if present)
            if generated_sql.startswith("```sql"):
                generated_sql = generated_sql[6:]
            if generated_sql.startswith("```"):
                generated_sql = generated_sql[3:]
            if generated_sql.endswith("```"):
                generated_sql = generated_sql[:-3]
            
            generated_sql = generated_sql.strip()
            
            # Ensure SQL ends with semicolon
            if not generated_sql.endswith(';'):
                generated_sql += ';'
            
            logger.info(f"Generated initial SQL [correlation_id={correlation_id}]: {generated_sql[:200]}...")
            
            # Create allowlist for validation
            allowlist_set = set(allowed_tables) if allowed_tables else set(self.schema_context.keys())
            
            # Validate the generated SQL
            validation_result = validate_sql(generated_sql, allowlist_set)
            
            if validation_result.ok:
                logger.info(f"SQL validation passed [correlation_id={correlation_id}]")
                return SqlGenResult(
                    sql=generated_sql,
                    issues=[],
                    meta={
                        "model": "gpt-4",
                        "repair_attempts": 0,
                        "generation_time_seconds": (datetime.now() - start_time).total_seconds(),
                        "validation_passed": True
                    },
                    correlation_id=correlation_id,
                    generated_at=datetime.now()
                )
            
            # SQL failed validation - attempt repairs
            logger.warning(f"SQL validation failed [correlation_id={correlation_id}]: {validation_result.issues}")
            issues.extend([issue.message for issue in validation_result.issues])
            
            # Attempt repairs
            current_sql = generated_sql
            for attempt_num in range(1, self.max_repair_attempts + 1):
                logger.info(f"Attempting SQL repair #{attempt_num} [correlation_id={correlation_id}]")
                
                repair_prompt = self._build_repair_prompt(
                    current_sql, 
                    str(validation_result.issues), 
                    [issue.message for issue in validation_result.issues]
                )
                
                repair_response = await self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": repair_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.1,
                    timeout=self.request_timeout
                )
                
                repaired_sql = repair_response.choices[0].message.content
                if repaired_sql is None:
                    repaired_sql = ""
                else:
                    repaired_sql = repaired_sql.strip()
                
                if not repaired_sql:
                    # Handle empty repair response
                    repair_attempts.append(RepairAttempt(
                        attempt_number=attempt_num,
                        original_error=str(validation_result.issues),
                        repair_prompt=repair_prompt,
                        generated_sql="",
                        success=False
                    ))
                    continue
                
                # Clean up repaired SQL
                if repaired_sql.startswith("```sql"):
                    repaired_sql = repaired_sql[6:]
                if repaired_sql.startswith("```"):
                    repaired_sql = repaired_sql[3:]
                if repaired_sql.endswith("```"):
                    repaired_sql = repaired_sql[:-3]
                
                repaired_sql = repaired_sql.strip()
                if not repaired_sql.endswith(';'):
                    repaired_sql += ';'
                
                # Validate repaired SQL
                repair_validation = validate_sql(repaired_sql, allowlist_set)
                
                repair_attempts.append(RepairAttempt(
                    attempt_number=attempt_num,
                    original_error=str(validation_result.issues),
                    repair_prompt=repair_prompt,
                    generated_sql=repaired_sql,
                    success=repair_validation.ok
                ))
                
                if repair_validation.ok:
                    logger.info(f"SQL repair #{attempt_num} succeeded [correlation_id={correlation_id}]")
                    return SqlGenResult(
                        sql=repaired_sql,
                        issues=[],
                        meta={
                            "model": "gpt-4",
                            "repair_attempts": attempt_num,
                            "generation_time_seconds": (datetime.now() - start_time).total_seconds(),
                            "validation_passed": True,
                            "repair_history": [
                                {
                                    "attempt": attempt.attempt_number,
                                    "success": attempt.success,
                                    "sql": attempt.generated_sql[:200] + "..." if len(attempt.generated_sql) > 200 else attempt.generated_sql
                                }
                                for attempt in repair_attempts
                            ]
                        },
                        correlation_id=correlation_id,
                        generated_at=datetime.now()
                    )
                
                # Update issues and current SQL for next attempt
                issues.extend([issue.message for issue in repair_validation.issues])
                current_sql = repaired_sql
                validation_result = repair_validation
                
                logger.warning(f"SQL repair #{attempt_num} failed [correlation_id={correlation_id}]: {repair_validation.issues}")
            
            # All repair attempts failed
            logger.error(f"All repair attempts failed [correlation_id={correlation_id}]")
            return SqlGenResult(
                sql=current_sql,
                issues=issues,
                meta={
                    "model": "gpt-4",
                    "repair_attempts": self.max_repair_attempts,
                    "generation_time_seconds": (datetime.now() - start_time).total_seconds(),
                    "validation_passed": False,
                    "repair_history": [
                        {
                            "attempt": attempt.attempt_number,
                            "success": attempt.success,
                            "error": attempt.original_error[:200] + "..." if len(attempt.original_error) > 200 else attempt.original_error
                        }
                        for attempt in repair_attempts
                    ]
                },
                correlation_id=correlation_id,
                generated_at=datetime.now()
            )
            
        except asyncio.TimeoutError:
            logger.error(f"OpenAI API timeout [correlation_id={correlation_id}]")
            return SqlGenResult(
                sql="",
                issues=["Request timeout - OpenAI API took too long to respond"],
                meta={
                    "model": "gpt-4",
                    "repair_attempts": 0,
                    "generation_time_seconds": (datetime.now() - start_time).total_seconds(),
                    "validation_passed": False,
                    "error": "timeout"
                },
                correlation_id=correlation_id,
                generated_at=datetime.now()
            )
        
        except Exception as e:
            logger.error(f"SQL generation error [correlation_id={correlation_id}]: {str(e)}")
            return SqlGenResult(
                sql="",
                issues=[f"SQL generation failed: {str(e)}"],
                meta={
                    "model": "gpt-4",
                    "repair_attempts": 0,
                    "generation_time_seconds": (datetime.now() - start_time).total_seconds(),
                    "validation_passed": False,
                    "error": str(e)
                },
                correlation_id=correlation_id,
                generated_at=datetime.now()
            )


# Global instance
sql_generator = SqlGenerator()
