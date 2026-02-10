# scripts/run_dev.py (без pyngrok зависимостей)
import subprocess
import time
import sys
import requests

def run_command(command, name):
    """Запуск команды в отдельном процессе"""
    print(f"🚀 Запуск {name}...")
    return subprocess.Popen(command, shell=True)

def start_development():
    print("🎮 ЗАПУСК РЕЖИМА РАЗРАБОТКИ ANIME CARDS GAME")
    print("=" * 50)
    
    # 1. Проверяем наличие .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Файл .env загружен")
    except:
        print("❌ Файл .env не найден")
        return
    
    processes = []
    
    try:
        # 2. Запускаем FastAPI
        api_cmd = "uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
        processes.append(run_command(api_cmd, "FastAPI"))
        time.sleep(3)
        
        print(f"\n📱 FastAPI запущен:")
        print(f"   Local:  http://localhost:8000")
        print(f"   Docs:   http://localhost:8000/docs")
        
        # 3. Запускаем бота (polling режим - БЕЗ вебхуков для разработки)
        print("\n🤖 Запуск Telegram бота в polling режиме...")
        print("   (Вебхуки не нужны для разработки)")
        
        bot_cmd = f"{sys.executable} -m src.bot.main"
        processes.append(run_command(bot_cmd, "Telegram Bot"))
        
        print("\n✅ Все сервисы запущены!")
        print("\n📋 Доступные команды в боте:")
        print("   /start - Начало")
        print("   /farm - Фармить монеты")
        print("   /collection - Коллекция карт")
        print("   /open_pack - Открыть пачку")
        print("   /upgrade - Улучшить карту")
        
        print("\n🛑 Для остановки нажмите Ctrl+C")
        
        # Держим процессы активными
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка всех процессов...")
        for proc in processes:
            proc.terminate()
        print("✅ Все процессы остановлены")

if __name__ == "__main__":
    start_development()