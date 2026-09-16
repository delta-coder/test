import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./cinema.db"
    secret_key: str = "dev-secret-change-me"
    allowed_origins: str = "*"
    hold_ttl_seconds: int = 120
    jwt_expire_hours: int = 72
    admin_username: str = "admin"
    admin_password: str = "123"
    admin_email: str = "admin@cinema.local"
    cookie_name: str = "cinema_token"
    cookie_secure: bool = False

    @property
    def origins_list(self) -> list[str]:
        raw = self.allowed_origins.strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


def _normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


@lru_cache
def get_settings() -> Settings:
    # Allow DATABASE_URL / SECRET_KEY from env without prefix
    data = {}
    db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    if db_url:
        data["database_url"] = _normalize_db_url(db_url)
    elif os.getenv("VERCEL"):
        # On Vercel serverless without remote DB, use writable /tmp
        data["database_url"] = "sqlite:////tmp/cinema.db"

    if os.getenv("SECRET_KEY"):
        data["secret_key"] = os.environ["SECRET_KEY"]
    if os.getenv("ALLOWED_ORIGINS"):
        data["allowed_origins"] = os.environ["ALLOWED_ORIGINS"]
    if os.getenv("HOLD_TTL_SECONDS"):
        data["hold_ttl_seconds"] = int(os.environ["HOLD_TTL_SECONDS"])
    if os.getenv("JWT_EXPIRE_HOURS"):
        data["jwt_expire_hours"] = int(os.environ["JWT_EXPIRE_HOURS"])
    if os.getenv("ADMIN_USERNAME"):
        data["admin_username"] = os.environ["ADMIN_USERNAME"]
    if os.getenv("ADMIN_PASSWORD"):
        data["admin_password"] = os.environ["ADMIN_PASSWORD"]
    if os.getenv("ADMIN_EMAIL"):
        data["admin_email"] = os.environ["ADMIN_EMAIL"]
    if os.getenv("COOKIE_SECURE"):
        data["cookie_secure"] = os.environ["COOKIE_SECURE"].lower() in {
            "1",
            "true",
            "yes",
        }
    if os.getenv("VERCEL"):
        data["cookie_secure"] = True
    return Settings(**data)

