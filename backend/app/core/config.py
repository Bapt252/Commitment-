from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Commitment API"
    
    # Configuration NLP
    SPACY_MODEL: str = "fr_core_news_lg"
    CAMEMBERT_MODEL: str = "camembert-base"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost", 
        "http://localhost:8080",
        "http://localhost:3000",
        "https://bapt252.github.io"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()