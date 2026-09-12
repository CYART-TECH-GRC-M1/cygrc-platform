import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "CyGRC Platform API"
    API_V1_STR: str = "/api/v1"
<<<<<<< HEAD
    SECRET_KEY: str = "cygrc_dev_secret_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
=======
    SECRET_KEY: str = "dev-only-change-me-CHANGE-THIS-BEFORE-ANYTHING-REAL"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
>>>>>>> origin/Abhishek

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "cygrc_db"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

<<<<<<< HEAD
    KEYCLOAK_ENABLED: bool = False
    LOCAL_AUTH_ENABLED: bool = True
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "cygrc"
    KEYCLOAK_CLIENT_ID: str = "cygrc-backend"
    KEYCLOAK_CLIENT_SECRET: Optional[str] = None
    KEYCLOAK_AUDIENCE: Optional[str] = None

    @property
    def keycloak_realm_url(self) -> str:
        return f"{self.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{self.KEYCLOAK_REALM}"
=======
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM_NAME: str = "cygrc"
    KEYCLOAK_CLIENT_ID: str = "cygrc-backend"
    KEYCLOAK_CLIENT_SECRET: str = ""
    KEYCLOAK_ENABLED: bool = True
    LOCAL_AUTH_ENABLED: bool = False
    KEYCLOAK_AUDIENCE: Optional[str] = None
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def async_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def keycloak_realm_url(self) -> str:
        return f"{self.KEYCLOAK_SERVER_URL}/realms/{self.KEYCLOAK_REALM_NAME}"
>>>>>>> origin/Abhishek

    @property
    def keycloak_jwks_url(self) -> str:
        return f"{self.keycloak_realm_url}/protocol/openid-connect/certs"

    @property
    def keycloak_token_url(self) -> str:
        return f"{self.keycloak_realm_url}/protocol/openid-connect/token"

<<<<<<< HEAD

    @property
    def async_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
=======
    @property
    def keycloak_userinfo_url(self) -> str:
        return f"{self.keycloak_realm_url}/protocol/openid-connect/userinfo"
>>>>>>> origin/Abhishek

    class Config:
        env_file = [
            os.path.join(BASE_DIR, ".env"),
            ".env",
            "backend/.env"
        ]
        extra = "ignore"


settings = Settings()
