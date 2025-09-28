# Story 001: Backend Foundation

**Epic:** E0 - Platform DevEx Epic  
**Priority:** P1  
**Labels:** `epic:E0`, `type:story`, `prio:P1`  
**Status:** Ready  

## Context

Create the foundational FastAPI backend skeleton with essential middleware, health checks, and database connectivity using ODBC Driver 18 for SQL Server. This establishes the core platform that all subsequent features will build upon.

The backend must support secure database connections with proper encryption settings, while allowing development flexibility with certificate handling for local environments.

## Story

**As a** developer working on the SQL Chatbot application  
**I want** a robust FastAPI backend foundation with health monitoring and secure database connectivity  
**So that** I can build all subsequent features on a reliable, well-configured platform

## Tasks

### Backend Setup
- [ ] Create FastAPI application skeleton with proper project structure
- [ ] Implement configuration loader supporting environment variables
- [ ] Add request-ID middleware for correlation tracking
- [ ] Set up CORS middleware for development

### Health Endpoints
- [ ] Implement `/healthz` endpoint returning 200 OK with basic health status
- [ ] Implement `/db/ping` endpoint testing database connectivity
- [ ] Add proper error handling for database connection failures

### Database Configuration  
- [ ] Configure ODBC Driver 18 DSN connection
- [ ] Set `Encrypt=yes` for secure connections
- [ ] Add dev-only `TrustServerCertificate=yes` option for self-signed certificates
- [ ] Test connectivity against AdventureWorks database

### Testing & Documentation
- [ ] Write unit tests for health endpoints
- [ ] Write integration tests for database connectivity
- [ ] Update `.env.example` with database configuration options
- [ ] Document ODBC 18 connection requirements

## Acceptance Criteria

1. **Server Startup:** FastAPI server boots successfully without errors
2. **Health Check:** `/healthz` endpoint returns 200 OK with health status JSON
3. **Database Ping:** `/db/ping` endpoint returns 200 OK when connected to AdventureWorks
4. **Error Handling:** Database connection failures return user-safe error messages (no stack traces)
5. **Configuration:** All database settings configurable via environment variables
6. **Security:** Production settings use encrypted connections; dev allows certificate flexibility
7. **Tests:** All tests pass locally and in CI with minimal coverage on new code

## Definition of Done

- [ ] Tests green locally and in CI; minimal coverage on new code
- [ ] Config/docs updated (`.env.example`, `README_dev.md`)  
- [ ] Logs include correlation IDs; errors are user-safe (no secrets, no stack dumps)
- [ ] DB connection string options documented (ODBC 18 `Encrypt=yes`; dev uses `TrustServerCertificate=yes` if self-signed)
- [ ] Security: connection parameters validated and sanitized
- [ ] Accessibility: N/A for backend-only story
- [ ] Performance: Health endpoints respond within 100ms under normal conditions

## Dev Notes

### Technical Requirements
- Use FastAPI with async/await patterns
- ODBC Driver 18 for SQL Server connectivity
- Environment-based configuration management
- Structured logging with correlation IDs

### Database Connection String Format
```
Driver={ODBC Driver 18 for SQL Server};Server=localhost,1433;Database=AdventureWorks;Uid=sa;Pwd=YourPassword123!;Encrypt=yes;TrustServerCertificate=yes;
```

### Known Considerations
- Dev environments may need `TrustServerCertificate=yes` for self-signed certificates
- Production should never use `TrustServerCertificate=yes`
- AdventureWorks database must be available in local Docker SQL Server

## Testing

### Unit Tests Required
- Health endpoint returns correct status codes and JSON structure
- Database ping handles connection success and failure scenarios
- Configuration loader parses environment variables correctly
- Request ID middleware adds correlation headers

### Integration Tests Required  
- End-to-end health check through HTTP client
- Database connectivity test against real AdventureWorks instance
- Configuration validation with various environment setups

### Test Data
- Use AdventureWorks sample database for database connectivity tests
- Mock database failures to test error handling paths

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Tasks Completed
- [ ] FastAPI skeleton setup
- [ ] Configuration loader implementation  
- [ ] Request-ID middleware
- [ ] Health endpoints (`/healthz`, `/db/ping`)
- [ ] Database ODBC configuration
- [ ] Unit tests
- [ ] Integration tests
- [ ] Documentation updates

### Debug Log References
_To be filled by dev agent with links to specific debug sessions_

### Completion Notes
_To be filled by dev agent with implementation details and decisions_

### File List
_To be filled by dev agent with all new/modified/deleted files_

### Change Log
_To be filled by dev agent with detailed changes made_
