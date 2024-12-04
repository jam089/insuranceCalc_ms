from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class DBConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 2


class ImportConfig(BaseModel):
    path: Path = BASE_DIR / "imports" / "import_rates.json"


class KafkaLoggerConfig(BaseModel):
    bootstrap_servers: str
    topic: str
    enable: bool = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env.template", ".env"],
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="insurance__",
    )

    run: RunConfig = RunConfig()
    import_: ImportConfig = ImportConfig()
    db: DBConfig
    kafka_logger: KafkaLoggerConfig


settings = Settings()
