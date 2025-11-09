"""Configuration Management for Ada Maritime AI"""

import os
from typing import Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration"""
    postgres_url: str
    redis_url: str
    qdrant_url: str
    neo4j_url: str
    neo4j_auth: str


@dataclass
class APIConfig:
    """API Keys configuration"""
    anthropic_api_key: str
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None


@dataclass
class AppConfig:
    """Application configuration"""
    environment: str
    debug: bool
    log_level: str
    
    database: DatabaseConfig
    api: APIConfig
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables"""
        
        # API Keys
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        api_config = APIConfig(
            anthropic_api_key=anthropic_key,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Database
        db_config = DatabaseConfig(
            postgres_url=os.getenv(
                "POSTGRES_URL",
                "postgresql://ada:ada_dev_password@localhost:5432/ada_ecosystem"
            ),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            neo4j_url=os.getenv("NEO4J_URL", "bolt://localhost:7687"),
            neo4j_auth=os.getenv("NEO4J_PASSWORD", "ada_dev_password")
        )
        
        # App settings
        environment = os.getenv("NODE_ENV", "development")
        
        return cls(
            environment=environment,
            debug=(environment == "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database=db_config,
            api=api_config
        )


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create global configuration"""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config
