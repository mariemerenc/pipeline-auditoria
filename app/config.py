from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    elasticsearch_url: str
    upload_dir: Path = Path("data/uploads")
    spacy_model: str = "pt_core_news_lg"
    embedding_model: str = "intfloat/multilingual-e5-small"
    chunk_tam: int = 800
    chunk_sobrepos: int = 100


settings = Settings()
