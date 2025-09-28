"""Configuration management for SQL Chatbot application."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Database Configuration
    db_server: str = "localhost"
    db_port: int = 1433
    db_name: str = "AdventureWorks2022"
    db_user: str = "sa"
    db_password: str = "YourStrong!Passw0rd"
    db_encrypt: str = "yes"
    db_trust_server_cert: str = "yes"  # dev only
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 800
    openai_request_timeout: int = 30
    openai_max_retries: int = 2
    
    # Application Configuration
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"
    
    # API Configuration
    request_id_header: str = "X-Request-ID"
    db_timeout_seconds: int = 5
    
    # SQL Validator Configuration
    sql_allowlist: str = "Sales.SalesOrderHeader,Sales.SalesOrderDetail,Production.Product,Person.Person"
    sql_max_rows: int = 5000
    sql_timeout_seconds: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_connection_string(self) -> str:
        """Build ODBC connection string from individual components."""
        return (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"Server={self.db_server},{self.db_port};"
            f"Database={self.db_name};"
            f"Uid={self.db_user};"
            f"Pwd={self.db_password};"
            f"Encrypt={self.db_encrypt};"
            f"TrustServerCertificate={self.db_trust_server_cert};"
        )
    
    @property
    def sql_allowlist_set(self) -> set[str]:
        """Parse SQL allowlist from comma-separated string to set."""
        return {table.strip() for table in self.sql_allowlist.split(",") if table.strip()}


# Global settings instance
settings = Settings()
