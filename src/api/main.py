from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.api import routes

# Создаем приложение
app = FastAPI(
    title="Anime Cards Game API",
    description="API для игрового карточного бота",
    version="1.0.0",
    debug=settings.APP_DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(routes.router)

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Anime Cards Game API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy"}
