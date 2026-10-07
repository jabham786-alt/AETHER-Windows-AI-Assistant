from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
 app_env:str="development";host:str="127.0.0.1";port:int=8765;ai_provider:str="openai";ai_model:str="gpt-4.1-mini";openai_api_key:str="";gemini_api_key:str="";database_url:str="sqlite:///./data/aether.db"
 model_config=SettingsConfigDict(env_file=".env",env_prefix="AETHER_",extra="ignore")
@lru_cache
def get_settings():return Settings()