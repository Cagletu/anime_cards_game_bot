from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from src.database.base import Base

class Card(Base):
    """Модель карточки из парсера"""
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, unique=True, index=True)
    local_path = Column(String, nullable=True)
    
    # Основная информация
    card_name = Column(String, index=True)
    character_name = Column(String, index=True)
    rarity = Column(String, index=True)  # SSS, ASS, S, A, B, C, D, E
    
    # Связанное аниме
    anime_name = Column(String, index=True)
    anime_link = Column(String)
    
    # Изображение
    image_data = Column(JSON)
    file_format = Column(String, default="webp")
    
    # Игровые статы (из RARITY_STATS)
    base_power = Column(Integer, default=100)
    base_health = Column(Integer, default=100)
    base_attack = Column(Integer, default=10)
    base_defense = Column(Integer, default=10)
    
    # Уровень и прогресс
    level = Column(Integer, default=1)
    max_level = Column(Integer, default=50)
    experience = Column(Integer, default=0)
    
    # Мета-данные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Card {self.card_name} ({self.rarity})>"
