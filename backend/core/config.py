import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "CyGRC Platform API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "cygrc_dev_secret_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "cygrc_db"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    ENVIRONMENT: str = "development"  # "development", "staging", "production", "test"
    ALLOW_DEV_TENANT_HEADER: bool = True

    TOKEN_ISSUER: Optional[str] = None
    TOKEN_AUDIENCE: Optional[str] = None

    KEYCLOAK_ENABLED: bool = False
    LOCAL_AUTH_ENABLED: bool = True
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "cygrc"
    KEYCLOAK_REALM_NAME: str = "cygrc"
    KEYCLOAK_CLIENT_ID: str = "cygrc-backend"
    KEYCLOAK_CLIENT_SECRET: Optional[str] = None
    KEYCLOAK_AUDIENCE: Optional[str] = None
    CORS_ORIGINS: str = "http://localhost:3000"

    # Threat Intelligence Integrations (Phase 6)
    MISP_URL: Optional[str] = None
    MISP_API_KEY: Optional[str] = None
    MISP_VERIFY_SSL: bool = True
    MISP_TIMEOUT: float = 30.0
    MISP_MAX_RETRIES: int = 3
    MISP_BACKOFF_FACTOR: float = 0.5

    OPENCTI_URL: Optional[str] = None
    OPENCTI_API_KEY: Optional[str] = None
    OPENCTI_VERIFY_SSL: bool = True
    OPENCTI_TIMEOUT: float = 30.0
    OPENCTI_MAX_RETRIES: int = 3
    OPENCTI_BACKOFF_FACTOR: float = 0.5

    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() == "production"

    @property
    def is_local_auth_allowed(self) -> bool:
        """Local fallback auth is strictly forbidden in production."""
        if self.is_production():
            return False
        return self.LOCAL_AUTH_ENABLED or not self.KEYCLOAK_ENABLED

    @property
    def is_dev_tenant_header_allowed(self) -> bool:
        """Arbitrary X-Tenant-ID headers without auth are strictly forbidden in production."""
        if self.is_production():
            return False
        return self.ALLOW_DEV_TENANT_HEADER

    @property
    def keycloak_realm_url(self) -> str:
        return f"{self.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{self.KEYCLOAK_REALM}"

    @property
    def keycloak_jwks_url(self) -> str:
        return f"{self.keycloak_realm_url}/protocol/openid-connect/certs"

    @property
    def keycloak_token_url(self) -> str:
        return f"{self.keycloak_realm_url}/protocol/openid-connect/token"

    @property
    def keycloak_userinfo_url(self) -> str:
        return f"{self.keycloak_realm_url}/protocol/openid-connect/userinfo"

    @property
    def async_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        if os.getenv("USE_SQLITE", "true").lower() == "true":
            return "sqlite+aiosqlite:///./cygrc.db"
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = [
            os.path.join(BASE_DIR, ".env"),
            ".env",
            "backend/.env"
        ]
        extra = "ignore"


settings = Settings()
