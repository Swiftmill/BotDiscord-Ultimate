from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Ultimate License Backend"
    database_url: str = Field(default=f"sqlite:///{(Path(__file__).resolve().parent / 'licenses.db').as_posix()}")
    secret_key: str = Field(default="change-me-super-secret-key")
    token_expiration_minutes: int = Field(default=60)
    rate_limit_per_minute: int = Field(default=60)
    antivirus_hash_db: Path = Field(default=Path(__file__).resolve().parent / "antivirus_hashes.txt")

    class Config:
        env_prefix = "ULB_"
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
