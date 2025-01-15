from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = Field(..., env="ENVIRONMENT", pattern=r"^(dev|ppr|prod)$")
    
    BACK_NAME: str = Field(..., env="BACK_NAME", min_length=3, max_length=15)
    BACK_VERSION: str = Field(..., env="BACK_VERSION", pattern=r"^\d+\.\d+\.\d+$")
    BACK_DESCRIPTION: str = Field(..., env="BACK_DESCRIPTION", min_length=3, max_length=50)
    
    BACK_LOG_MAX_BYTES: int = Field(..., env = "BACK_LOG_MAX_BYTES")
    BACK_BACKUP_COUNT: int = Field(..., env="BACK_BACKUP_COUNT")
    
    model_config = SettingsConfigDict(env_file=".env")
    
    
@lru_cache
def get_settings() -> Settings:
    return Settings()

