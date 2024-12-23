from pathlib import Path
from typing import List

from pydantic import BaseModel, PostgresDsn, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8050
    reload: bool = True


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 2


class KafkaConfig(BaseModel):
    bootstrap_servers: str
    topics: List
    max_records: int = 10
    fetch_min_bytes: int = 2024


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ],
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="consumer__",
    )

    run: RunConfig = RunConfig()
    db: DatabaseConfig
    kafka: KafkaConfig


settings = Settings()
