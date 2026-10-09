from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8765
    ai_provider: str = "openai"
    ai_model: str = "gpt-4.1-mini"
    stt_provider: str = "local-whisper"
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")
    deepgram_api_key: str = Field(default="", validation_alias="DEEPGRAM_API_KEY")
    tavily_api_key: str = Field(default="", validation_alias="TAVILY_API_KEY")
    google_oauth_client_file: str = "backend/data/google_oauth_client.json"
    google_token_file: str = "backend/data/google_token.json"
    database_url: str = "sqlite:///./data/aether.db"
    model_config = SettingsConfigDict(env_file=".env", env_prefix="AETHER_", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
