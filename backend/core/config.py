from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy.orm import DeclarativeBase


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./cygrc.db")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"}


settings = Settings()


class Base(DeclarativeBase):
    pass
