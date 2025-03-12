import os
import sys
from typing import Optional

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    if sys.platform.lower() == "win32" or os.name.lower() in ["nt", "darwin", "posix"]:
        from dotenv import load_dotenv

        load_dotenv()
    postgres_user: str = Field(os.environ.get("POSTGRES_USER"))
    postgres_password: str = Field(os.environ.get("POSTGRES_PASSWORD"))
    postgres_host: str = Field(os.environ.get("POSTGRES_HOST"))
    postgres_port: int = Field(os.environ.get("POSTGRES_PORT"))
    postgres_db: str = Field(os.environ.get("POSTGRES_DB"))

    project_name: str = Field(os.environ.get("PROJECT_NAME"))
    project_description: str = Field(os.environ.get("PROJECT_DESCRIPTION"))
    project_version: str = Field(os.environ.get("PROJECT_VERSION"))
    is_debug_mode: bool = Field(os.environ.get("DEBUG_MODE"))

    secret_key: str = Field(os.environ.get("SECRET_KEY"))
    algorithm: str = Field(os.environ.get("ALGORITHM"))
    access_token_expire_minutes: int = Field(
        os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    )
    refresh_token_expire_days: int = Field(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS"))

    @property
    def database_url(self) -> Optional[PostgresDsn]:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings: Settings | None = None


def get_settings() -> Settings:
    """
    Возвращает глобальные настройки проекта
    """
    global settings

    if not settings:
        settings = Settings()
    return settings
