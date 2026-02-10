from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ADMIN_ID: int
    
    # FastAPI
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True
    
    # # Game
    # STARTING_CARDS: int = 5
    # DAILY_REWARDS: int = 3
    # MAX_DECK_SIZE: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
