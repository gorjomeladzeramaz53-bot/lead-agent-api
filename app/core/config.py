from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lead Agent API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite+aiosqlite:///./lead_agent.db"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

def get_settings() -> Settings:
    return Settings()