# E0: Platform & DevEx (Enabler Epic)

## Epic Goal

Establish robust development foundation and infrastructure runway to enable all subsequent SQL Chatbot visualization enhancement work while maintaining compatibility with existing FastAPI/SQL Server architecture.

## Epic Description

**Existing System Context:**

- Current functionality: Basic SQL Chatbot POC with FastAPI backend, simple HTML frontend, GPT-5 integration, SQL Server connectivity
- Technology stack: Python 3.11, FastAPI 0.103.1, HTML/CSS/JS, ODBC 18+, AdventureWorks database
- Integration points: GPT-5 API calls, SQL Server database connections, static file serving

**Enhancement Details:**

- What's being added/changed: Repository scaffolding, enhanced FastAPI structure, CI/lint/tests, secure ODBC 18+ connectivity with TLS configuration
- How it integrates: Extends existing FastAPI application structure with new modules for validation, visualization, and configuration management
- Success criteria: Complete development environment setup, robust database connectivity, comprehensive testing framework, automated quality gates

## Stories

1. **Story E0.1:** Repository Scaffolding & Project Structure
   - Create enhanced directory structure with config/, tests/, and organized app/ modules
   - Establish development environment documentation and setup scripts
   - Configure .env templates for development and production environments

2. **Story E0.2:** Enhanced FastAPI Foundation & CI/CD Pipeline  
   - Extend existing FastAPI application with new response schemas and endpoint structure
   - Implement comprehensive testing framework with unit, integration, and accessibility tests
   - Set up automated linting, type checking, and security validation

3. **Story E0.3:** Secure ODBC 18+ Database Connectivity
   - Enhance existing database connection with configurable TLS options (Encrypt=Yes, TrustServerCertificate)
   - Implement connection pooling and error handling improvements
   - Create database schema validation and least-privilege service account setup

## Dependencies

**Blocks:** E1 (SQL Safety Layer), E2 (LLM→SQL Tooling), E3 (Visualization Sandbox), E4 (Visualize UI)

**Dependency Rationale:** All subsequent development requires the enhanced project structure, secure database connectivity, and testing framework established in this enabler epic.

## Compatibility Requirements

- [x] Maintain existing FastAPI endpoint compatibility
- [x] Preserve existing GPT-5 API integration patterns  
- [x] Ensure SQL Server container connectivity remains functional
- [x] Keep existing static file serving operational during enhancement

## Risk Mitigation

- **Primary Risk:** ODBC 18+ TLS configuration changes break existing database connectivity
- **Mitigation:** Provide comprehensive environment configuration documentation and troubleshooting guides for common certificate issues
- **Rollback Plan:** Maintain existing connection string configuration as fallback option with clear documentation

## Definition of Done

- [x] Enhanced project structure implemented with all required directories and modules
- [x] Comprehensive testing framework operational with automated CI/CD pipeline
- [x] ODBC 18+ connectivity working with both development (self-signed) and production certificate configurations
- [x] Development environment documentation complete with setup guides and troubleshooting
- [x] Existing functionality verified through automated regression testing
- [x] All code quality gates (linting, type checking, security validation) passing

## Integration Verification

- **IV-E0-01:** Existing natural language query processing continues to function without modification
- **IV-E0-02:** Current SQL Server connectivity maintains performance characteristics
- **IV-E0-03:** GPT-5 API integration patterns remain operational
- **IV-E0-04:** Static file serving continues to work for existing HTML/CSS/JS assets
