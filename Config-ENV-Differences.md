# Story 003: Configuration & Environment Differences

This document outlines the configuration changes and environment variable updates introduced in Story 003.

## Environment Variables Added

### New Variables in `.env.example`

```bash
# OpenAI Configuration (NEW)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Database Configuration - Enhanced (MODIFIED)
# Requires Microsoft ODBC Driver 18 for SQL Server installed
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=AdventureWorks2022
DB_USER=sa
DB_PASSWORD=your_secure_password_here

# Database Security - Enhanced with ODBC 18 Settings (NEW)
DB_ENCRYPT=yes
# SECURITY WARNING: TrustServerCertificate=yes is for DEVELOPMENT ONLY!
# In production, use proper SSL certificates and set to 'no'
DB_TRUST_SERVER_CERT=yes

# Application Configuration (EXISTING - documented)
LOG_LEVEL=INFO
REQUEST_ID_HEADER=X-Request-ID
DB_TIMEOUT_SECONDS=5

# SQL Validator Configuration - Enhanced (MODIFIED)
# Comma-separated list of allowed tables/views (schema.table format)
SQL_ALLOWLIST=Sales.SalesOrderHeader,Sales.SalesOrderDetail,Production.Product,Person.Person
SQL_MAX_ROWS=5000
SQL_TIMEOUT_SECONDS=30

# CORS Configuration (EXISTING)
# Add your frontend URL here
# CORS_ORIGINS=["http://localhost:3000"]
```

## Configuration File Changes

### `app/config.py` - New Settings Added

```python
# New OpenAI Configuration
openai_api_key: str = Field(..., description="OpenAI API key for LLM integration")
openai_model: str = Field(default="gpt-4", description="OpenAI model to use")

# Enhanced Database Configuration with ODBC Driver 18
db_encrypt: str = Field(default="yes", description="Database encryption setting")
db_trust_server_cert: str = Field(default="no", description="Trust server certificate setting")

# New SQL Generation Settings
sql_generation_timeout: int = Field(default=30, description="SQL generation timeout in seconds")
max_repair_attempts: int = Field(default=3, description="Maximum SQL repair attempts")
```

## Development vs Production Configuration

### Development Environment
```bash
# Development - Relaxed SSL for local SQL Server
DB_ENCRYPT=yes
DB_TRUST_SERVER_CERT=yes  # OK for local development
OPENAI_MODEL=gpt-4
LOG_LEVEL=DEBUG

# Development - Expanded table allowlist
SQL_ALLOWLIST=Production.Product,Production.ProductCategory,Production.ProductSubcategory,Sales.Customer,Sales.SalesOrderHeader,Sales.SalesOrderDetail,Person.Person,Person.Address
```

### Production Environment
```bash
# Production - Strict SSL validation
DB_ENCRYPT=yes
DB_TRUST_SERVER_CERT=no  # REQUIRED for production security
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO

# Production - Restricted table allowlist
SQL_ALLOWLIST=Production.Product,Sales.SalesOrderHeader,Sales.SalesOrderDetail
SQL_MAX_ROWS=1000  # Lower limit for production
```

## Docker Configuration Changes

### `docker-compose.yml` Additions (if applicable)

```yaml
services:
  sql-chatbot:
    environment:
      # OpenAI Configuration
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=gpt-4
      
      # Enhanced Database Configuration
      - DB_ENCRYPT=yes
      - DB_TRUST_SERVER_CERT=${DB_TRUST_SERVER_CERT:-no}
      
      # SQL Generation Configuration
      - SQL_TIMEOUT_SECONDS=30
      - SQL_MAX_ROWS=${SQL_MAX_ROWS:-5000}
```

## Infrastructure Dependencies

### Required System Components

#### ODBC Driver 18 for SQL Server
```bash
# Windows Installation
# Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Linux Installation (Ubuntu/Debian)
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Docker Installation
FROM python:3.11-slim
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

#### Python Dependencies Added
```bash
# New dependencies in requirements.txt
openai>=1.0.0          # OpenAI API client with structured outputs support
pyodbc>=4.0.39         # SQL Server ODBC connectivity
asyncio-extras>=1.3.2  # Enhanced async support for LLM operations
```

## Security Configuration Changes

### SSL/TLS Configuration

#### Development (Local SQL Server)
```bash
# Acceptable for local development only
DB_ENCRYPT=yes
DB_TRUST_SERVER_CERT=yes
```

#### Staging/Production (Remote SQL Server)
```bash
# Required for production security
DB_ENCRYPT=yes
DB_TRUST_SERVER_CERT=no  # Requires proper SSL certificates

# Additional production security
SQL_MAX_ROWS=1000        # Reduced resource limits
SQL_TIMEOUT_SECONDS=15   # Reduced timeout limits
LOG_LEVEL=INFO          # Reduced logging verbosity
```

### API Key Management

#### Development
```bash
# Local development - store in .env file (gitignored)
OPENAI_API_KEY=sk-your-key-here
```

#### Production
```bash
# Production - use secure secret management
# AWS: Store in AWS Secrets Manager or Parameter Store
# Azure: Store in Azure Key Vault
# Kubernetes: Store in Kubernetes secrets

# Environment injection in production
OPENAI_API_KEY=$(aws secretsmanager get-secret-value --secret-id openai-api-key --query SecretString --output text)
```

## Monitoring & Observability Configuration

### Logging Enhancements
```bash
# Enhanced logging configuration
LOG_LEVEL=INFO
REQUEST_ID_HEADER=X-Request-ID

# New correlation tracking
CORRELATION_ID_HEADER=X-Correlation-ID  # Auto-generated UUID tracking
SQL_EXECUTION_LOGGING=true             # Log all SQL generation and execution
```

### Health Check Configuration
```bash
# Health check endpoint configuration
HEALTH_CHECK_TIMEOUT=5                 # Seconds for database health checks
OPENAI_HEALTH_CHECK=true               # Include OpenAI API connectivity in health
```

## Performance Tuning Configuration

### SQL Generation Performance
```bash
# OpenAI API Configuration
OPENAI_TIMEOUT=30                      # API request timeout
OPENAI_MAX_TOKENS=800                  # Max tokens for structured output
OPENAI_TEMPERATURE=0.1                 # Low temperature for deterministic SQL

# Repair Pipeline Configuration
MAX_REPAIR_ATTEMPTS=3                  # Maximum SQL repair attempts
REPAIR_TIMEOUT=10                      # Timeout per repair attempt
```

### Database Performance
```bash
# Connection Pool Configuration
DB_CONNECTION_TIMEOUT=30               # Connection establishment timeout
DB_COMMAND_TIMEOUT=300                 # SQL execution timeout (5 minutes)
DB_MAX_POOL_SIZE=10                    # Maximum connection pool size

# Query Performance Limits
SQL_MAX_ROWS=5000                      # Maximum result set size
QUERY_BATCH_SIZE=1000                  # Batch size for result fetching
```

## Migration Guide

### From Story 002 to Story 003

#### Required Actions
1. **Install ODBC Driver 18**: Download and install Microsoft ODBC Driver 18 for SQL Server
2. **Add OpenAI API Key**: Obtain and configure OpenAI API key
3. **Update Environment Variables**: Add new variables to `.env` file
4. **Update Dependencies**: Run `pip install -r requirements.txt` to install new packages
5. **Test Database Connectivity**: Verify SSL settings work with your SQL Server instance

#### Migration Script
```bash
#!/bin/bash
# Story 003 Migration Script

echo "Migrating from Story 002 to Story 003..."

# Backup existing configuration
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Add new environment variables
echo "# OpenAI Configuration" >> .env
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
echo "OPENAI_MODEL=gpt-4" >> .env
echo "" >> .env
echo "# Enhanced Database Configuration" >> .env
echo "DB_ENCRYPT=yes" >> .env
echo "DB_TRUST_SERVER_CERT=yes" >> .env

# Install new dependencies
pip install -r requirements.txt

# Test configuration
python -c "from app.config import settings; print('Configuration loaded successfully')"

echo "Migration complete! Please update OPENAI_API_KEY in .env file"
```

## Troubleshooting Common Configuration Issues

### ODBC Driver Issues
```bash
# Error: "Data source name not found and no default driver specified"
# Solution: Install ODBC Driver 18 for SQL Server

# Error: "SSL Provider: The certificate chain was issued by an authority that is not trusted"
# Solution: Set DB_TRUST_SERVER_CERT=yes for development, or install proper SSL certificates for production
```

### OpenAI API Issues
```bash
# Error: "Invalid API key provided"
# Solution: Verify OPENAI_API_KEY is correctly set and valid

# Error: "Rate limit exceeded"
# Solution: Implement exponential backoff or upgrade OpenAI subscription tier

# Error: "Context length exceeded" 
# Solution: Reduce schema context or increase max_tokens setting
```

### Database Connection Issues
```bash
# Error: "Connection timeout expired"
# Solution: Increase DB_CONNECTION_TIMEOUT or verify network connectivity

# Error: "Login failed for user"
# Solution: Verify DB_USER and DB_PASSWORD are correct and user has necessary permissions
```

---

**Configuration completed for**: Story 003 - LLM to SQL Wrapper  
**Date**: September 28, 2025  
**Status**: Ready for Production Deployment
