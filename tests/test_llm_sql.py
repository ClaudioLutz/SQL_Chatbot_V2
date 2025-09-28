"""
Tests for LLM SQL generation service.

This module tests the SQL generation functionality including:
- Basic SQL generation from natural language
- Error repair and validation integration
- Schema context handling
- Pagination logic
- Edge cases and error scenarios
"""

import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.llm.sql_generator import SqlGenerator, SqlGenResult
from app.validation.sql_validator import ValidationResult, ValidationIssue


class TestSqlGenerator:
    """Test cases for SqlGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SqlGenerator()
        
        # Mock OpenAI client
        self.mock_client = AsyncMock()
        self.generator.client = self.mock_client
    
    @pytest.mark.asyncio
    async def test_generate_sql_success(self):
        """Test successful SQL generation with valid response."""
        # Mock structured output
        mock_structured = {
            "tables": [{"name": "Production.Product", "alias": "p"}],
            "columns": [
                {"table": "p", "name": "ProductID", "alias": None, "function": None},
                {"table": "p", "name": "Name", "alias": None, "function": None}
            ],
            "where_conditions": [],
            "joins": [],
            "order_by": [{"column": "p.ProductID", "direction": "ASC"}],
            "pagination": {"offset": 0, "fetch_next": 20}
        }
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(mock_structured)
        mock_response.choices = [mock_choice]
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Mock validation success
        with patch('app.llm.sql_generator.validate_sql') as mock_validate:
            mock_validate.return_value = ValidationResult(ok=True, issues=[], objects={'Production.Product'})
            
            result = await self.generator.generate_sql(
                prompt="Show me products",
                page=1,
                page_size=20,
                allowed_tables=['Production.Product']
            )
            
            assert isinstance(result, SqlGenResult)
            assert result.sql.endswith(';')
            assert 'Production.Product' in result.sql
            assert 'OFFSET 0 ROWS' in result.sql
            assert 'FETCH NEXT 20 ROWS ONLY' in result.sql
            assert result.issues == []
            assert result.meta['validation_passed'] == True
            assert result.meta['repair_attempts'] == 0
    
    @pytest.mark.asyncio
    async def test_generate_sql_with_pagination(self):
        """Test SQL generation with different pagination parameters."""
        # Mock structured output with pagination
        mock_structured = {
            "tables": [{"name": "Production.Product", "alias": "p"}],
            "columns": [
                {"table": "p", "name": "ProductID", "alias": None, "function": None},
                {"table": "p", "name": "Name", "alias": None, "function": None}
            ],
            "where_conditions": [],
            "joins": [],
            "order_by": [{"column": "p.ProductID", "direction": "ASC"}],
            "pagination": {"offset": 40, "fetch_next": 10}
        }
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(mock_structured)
        mock_response.choices = [mock_choice]
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Mock validation success
        with patch('app.llm.sql_generator.validate_sql') as mock_validate:
            mock_validate.return_value = ValidationResult(ok=True, issues=[], objects={'Production.Product'})
            
            result = await self.generator.generate_sql(
                prompt="Show me products",
                page=5,  # (5-1) * 10 = 40 offset
                page_size=10,
                allowed_tables=['Production.Product']
            )
            
            assert 'OFFSET 40 ROWS' in result.sql
            assert 'FETCH NEXT 10 ROWS ONLY' in result.sql
    
    @pytest.mark.asyncio
    async def test_generate_sql_with_repair(self):
        """Test SQL generation with repair functionality."""
        # Mock initial structured response (will fail validation)
        mock_structured_invalid = {
            "tables": [{"name": "Production.Product"}],
            "columns": [
                {"table": "Production.Product", "name": "ProductID"},
                {"table": "Production.Product", "name": "Name"}
            ],
            "where_conditions": [],
            "joins": [],
            "order_by": [{"column": "ProductID", "direction": "ASC"}],
            "pagination": {"offset": 0, "fetch_next": 20}
        }
        
        # Mock initial invalid response
        mock_response_1 = MagicMock()
        mock_choice_1 = MagicMock()
        mock_choice_1.message.content = json.dumps(mock_structured_invalid)
        mock_response_1.choices = [mock_choice_1]
        
        # Mock repaired SQL (plain text for repair)
        mock_response_2 = MagicMock()
        mock_choice_2 = MagicMock()
        mock_choice_2.message.content = "SELECT ProductID, Name FROM Production.Product ORDER BY ProductID OFFSET 0 ROWS FETCH NEXT 20 ROWS ONLY"
        mock_response_2.choices = [mock_choice_2]
        
        self.mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
        
        # Mock validation - first fails, second succeeds
        with patch('app.llm.sql_generator.validate_sql') as mock_validate:
            validation_issue = ValidationIssue(code="E_NO_ORDER_BY", message="ORDER BY required for deterministic results")
            mock_validate.side_effect = [
                ValidationResult(ok=False, issues=[validation_issue], objects={'Production.Product'}),
                ValidationResult(ok=True, issues=[], objects={'Production.Product'})
            ]
            
            result = await self.generator.generate_sql(
                prompt="Show me products",
                page=1,
                page_size=20,
                allowed_tables=['Production.Product']
            )
            
            assert result.sql.endswith(';')
            assert 'ORDER BY' in result.sql
            assert result.issues == []
            assert result.meta['validation_passed'] == True
            assert result.meta['repair_attempts'] == 1
            assert 'repair_history' in result.meta
    
    @pytest.mark.asyncio
    async def test_generate_sql_repair_failure(self):
        """Test SQL generation when repair attempts fail."""
        # Mock structured response that will always fail validation
        mock_structured_invalid = {
            "tables": [{"name": "NonExistentTable"}],
            "columns": [
                {"table": "NonExistentTable", "name": "ProductID"},
                {"table": "NonExistentTable", "name": "Name"}
            ],
            "where_conditions": [],
            "joins": [],
            "order_by": [{"column": "ProductID", "direction": "ASC"}],
            "pagination": {"offset": 0, "fetch_next": 20}
        }
        
        # Mock initial structured response
        mock_response_1 = MagicMock()
        mock_choice_1 = MagicMock()
        mock_choice_1.message.content = json.dumps(mock_structured_invalid)
        mock_response_1.choices = [mock_choice_1]
        
        # Mock repair responses that also fail
        mock_response_repair = MagicMock()
        mock_choice_repair = MagicMock()
        mock_choice_repair.message.content = "SELECT ProductID, Name FROM NonExistentTable"
        mock_response_repair.choices = [mock_choice_repair]
        
        self.mock_client.chat.completions.create.side_effect = [
            mock_response_1, mock_response_repair, mock_response_repair, mock_response_repair
        ]
        
        # Mock validation always fails
        with patch('app.llm.sql_generator.validate_sql') as mock_validate:
            validation_issue = ValidationIssue(code="E_NOT_ALLOWLIST", message="Table not in allowlist")
            mock_validate.return_value = ValidationResult(ok=False, issues=[validation_issue], objects={'NonExistentTable'})
            
            result = await self.generator.generate_sql(
                prompt="Show me data",
                page=1,
                page_size=20,
                allowed_tables=['Production.Product']
            )
            
            assert len(result.issues) > 0
            assert result.meta['validation_passed'] == False
            assert result.meta['repair_attempts'] == 3  # max attempts
    
    @pytest.mark.asyncio
    async def test_generate_sql_empty_response(self):
        """Test handling of empty response from OpenAI."""
        # Mock empty response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = None
        mock_response.choices = [mock_choice]
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = await self.generator.generate_sql(
            prompt="Show me products",
            page=1,
            page_size=20,
            allowed_tables=['Production.Product']
        )
        
        assert result.sql == ""
        assert "Empty response from OpenAI API" in result.issues
        assert result.meta['validation_passed'] == False
    
    @pytest.mark.asyncio
    async def test_generate_sql_timeout_error(self):
        """Test handling of timeout errors."""
        # Mock timeout
        self.mock_client.chat.completions.create.side_effect = asyncio.TimeoutError()
        
        result = await self.generator.generate_sql(
            prompt="Show me products",
            page=1,
            page_size=20,
            allowed_tables=['Production.Product']
        )
        
        assert result.sql == ""
        assert any("timeout" in issue.lower() for issue in result.issues)
        assert result.meta['error'] == 'timeout'
    
    @pytest.mark.asyncio
    async def test_generate_sql_api_error(self):
        """Test handling of API errors."""
        # Mock API error
        self.mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = await self.generator.generate_sql(
            prompt="Show me products",
            page=1,
            page_size=20,
            allowed_tables=['Production.Product']
        )
        
        assert result.sql == ""
        assert any("failed" in issue.lower() for issue in result.issues)
        assert "API Error" in str(result.meta.get('error', ''))
    
    def test_build_system_prompt(self):
        """Test system prompt building with schema context."""
        prompt = self.generator._build_system_prompt(['Production.Product', 'Production.ProductCategory'])
        
        assert 'Production.Product' in prompt
        assert 'Production.ProductCategory' in prompt
        assert 'T-SQL' in prompt
        assert 'ORDER BY' in prompt
        assert 'OFFSET' in prompt
        assert 'FETCH NEXT' in prompt
        assert 'AdventureWorks' in prompt
    
    def test_build_repair_prompt(self):
        """Test repair prompt building."""
        original_query = "SELECT ProductID FROM Production.Product"
        error_message = "ORDER BY required"
        validation_issues = ["ORDER BY clause missing"]
        
        prompt = self.generator._build_repair_prompt(original_query, error_message, validation_issues)
        
        assert original_query in prompt
        assert error_message in prompt
        assert "ORDER BY clause" in prompt
        assert "REPAIR CONSTRAINTS" in prompt
    
    def test_schema_context_completeness(self):
        """Test that schema context includes all required AdventureWorks tables."""
        expected_tables = [
            'Production.Product',
            'Production.ProductCategory',
            'Sales.Customer',
            'Sales.SalesOrderHeader',
            'Person.Person'
        ]
        
        for table in expected_tables:
            assert table in self.generator.schema_context
            assert 'columns' in self.generator.schema_context[table]
            assert 'description' in self.generator.schema_context[table]
    
    @pytest.mark.asyncio
    async def test_sql_cleanup(self):
        """Test SQL cleanup functionality (removing code blocks, adding semicolons)."""
        # Test the _ensure_single_statement method directly
        test_cases = [
            ("```sql\nSELECT 1\n```", "SELECT 1;"),
            ("```\nSELECT 1\n```", "SELECT 1;"),
            ("SELECT 1", "SELECT 1;"),
            ("SELECT 1;", "SELECT 1;"),  # Already has semicolon
            ("SELECT 1; SELECT 2;", "SELECT 1;"),  # Multi-statement test
        ]
        
        for input_sql, expected_sql in test_cases:
            cleaned_sql = self.generator._ensure_single_statement(input_sql)
            assert cleaned_sql == expected_sql
    
    @pytest.mark.asyncio
    async def test_correlation_id_tracking(self):
        """Test that correlation IDs are properly generated and tracked."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "SELECT 1"
        mock_response.choices = [mock_choice]
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Mock validation success
        with patch('app.llm.sql_generator.validate_sql') as mock_validate:
            mock_validate.return_value = ValidationResult(ok=True, issues=[], objects=set())
            
            result = await self.generator.generate_sql(
                prompt="test",
                page=1,
                page_size=20
            )
            
            assert result.correlation_id is not None
            assert len(result.correlation_id) > 0
            assert isinstance(result.generated_at, datetime)


@pytest.mark.asyncio
async def test_global_sql_generator_instance():
    """Test that the global sql_generator instance is properly configured."""
    from app.llm.sql_generator import sql_generator
    
    assert sql_generator is not None
    assert isinstance(sql_generator, SqlGenerator)
    assert sql_generator.max_repair_attempts == 3
    assert sql_generator.request_timeout == 30
    assert len(sql_generator.schema_context) > 0


class TestSqlGenResult:
    """Test cases for SqlGenResult dataclass."""
    
    def test_sql_gen_result_creation(self):
        """Test SqlGenResult can be created with all required fields."""
        result = SqlGenResult(
            sql="SELECT 1;",
            issues=[],
            meta={"test": True},
            correlation_id="test-id",
            generated_at=datetime.now()
        )
        
        assert result.sql == "SELECT 1;"
        assert result.issues == []
        assert result.meta["test"] == True
        assert result.correlation_id == "test-id"
        assert isinstance(result.generated_at, datetime)
    
    def test_sql_gen_result_with_issues(self):
        """Test SqlGenResult with validation issues."""
        issues = ["ORDER BY required", "Invalid table name"]
        
        result = SqlGenResult(
            sql="SELECT * FROM invalid_table",
            issues=issues,
            meta={"validation_passed": False},
            correlation_id="test-id",
            generated_at=datetime.now()
        )
        
        assert len(result.issues) == 2
        assert "ORDER BY required" in result.issues
        assert result.meta["validation_passed"] == False
