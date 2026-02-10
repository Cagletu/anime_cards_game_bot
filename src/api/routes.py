from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.base import get_db

router = APIRouter(prefix="/api/v1", tags=["api"])

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Получить статистику игры"""
    # Здесь будет логика получения статистики
    return {
        "total_cards": 0,
        "total_users": 0,
        "total_battles": 0
    }