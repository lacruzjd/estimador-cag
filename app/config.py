from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    LLM_PROVIDER: str
    LLM_MODEL: str
    APP_ENV: str
    LOG_LEVEL: str

    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
