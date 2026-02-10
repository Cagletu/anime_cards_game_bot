# scripts/dev.py
import subprocess
import time
import sys
import os
import requests
from datetime import datetime

def print_header():
    """Красивый заголовок"""
    print("\n" + "="*60)
    print("🎮 ANIME CARDS GAME - РЕЖИМ РАЗРАБОТКИ")
    print("="*60)

def run_command(command, name, wait_seconds=0):
    """Запуск команды в отдельном процессе"""
    print(f"🚀 Запуск {name}...")
    print(f"   Команда: {command}")
    
    # Для Windows используем CREATE_NEW_CONSOLE чтобы видеть вывод
    if sys.platform == "win32":
        process = subprocess.Popen(
            command,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    if wait_seconds > 0:
        time.sleep(wait_seconds)
    
    return process

def start_ngrok_tunnel(port=8000):
    """Запуск Ngrok туннеля (способ 1 - установленный ngrok)"""
    print("\n🌐 Запуск Ngrok туннеля...")
    
    # Проверяем установлен ли ngrok
    try:
        subprocess.run(["ngrok", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        print("❌ Ngrok не найден в PATH")
        print("   Скачайте с https://ngrok.com/download и добавьте в PATH")
        print("   или установите рядом с проектом")
        return None, None
    
    # Запускаем ngrok
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Ждем запуска
    time.sleep(3)
    
    # Получаем URL через Ngrok API
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json()
            public_url = tunnels["tunnels"][0]["public_url"]
            print(f"✅ Ngrok запущен: {public_url}")
            return ngrok_process, public_url
    except requests.RequestException:
        print("⚠️ Не удалось получить URL от Ngrok API")
        print("   Проверьте: http://localhost:4040")
    
    return ngrok_process, "http://localhost:4040"

def setup_webhook(bot_token, webhook_url):
    """Настройка вебхука для бота"""
    print(f"\n🔗 Настройка вебхука...")
    
    webhook_api = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {
        "url": f"{webhook_url}/webhook",
        "drop_pending_updates": True
    }
    
    try:
        response = requests.post(webhook_api, json=payload, timeout=10)
        if response.json().get("ok"):
            print("✅ Вебхук установлен")
            return True
        else:
            print(f"❌ Ошибка вебхука: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def start_development(use_webhook=False):
    """Запуск всех сервисов для разработки"""
    print_header()
    
    # Проверяем .env
    if not os.path.exists(".env"):
        print("❌ Файл .env не найден!")
        print("   Создайте .env из .env.example")
        return
    
    print("✅ Файл .env найден")
    
    processes = []
    ngrok_process = None
    webhook_url = None
    
    try:
        # 1. Запускаем FastAPI
        api_command = f"uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
        processes.append(run_command(api_command, "FastAPI API", 3))
        
        print(f"\n📱 FastAPI запущен:")
        print(f"   Локально:  http://localhost:8000")
        print(f"   Документация: http://localhost:8000/docs")
        print(f"   Альтернативная: http://localhost:8000/redoc")
        
        # 2. Запускаем Ngrok если нужен вебхук
        if use_webhook:
            ngrok_process, public_url = start_ngrok_tunnel(8000)
            if public_url:
                webhook_url = public_url
                
                # Настраиваем вебхук
                from dotenv import load_dotenv
                load_dotenv()
                bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
                if bot_token and bot_token != "your_token_here":
                    setup_webhook(bot_token, webhook_url)
                    
                    # Запускаем бота в вебхук режиме
                    bot_command = f"{sys.executable} src/bot/webhook_server.py"
                    processes.append(run_command(bot_command, "Telegram Bot (Webhook)", 2))
                else:
                    print("⚠️ TELEGRAM_BOT_TOKEN не настроен, запускаю polling")
                    use_webhook = False
        
        # 3. Если не вебхук - запускаем polling
        if not use_webhook:
            print("\n🤖 Запуск Telegram бота в polling режиме...")
            bot_command = f"{sys.executable} -m src.bot.main"
            processes.append(run_command(bot_command, "Telegram Bot (Polling)", 2))
            
            print("   ⚠️  Polling режим - для продакшена нужен вебхук")
            print("   🔧 Для вебхука запустите: python scripts/dev.py --webhook")
        
        # 4. Показываем итог
        print("\n" + "="*60)
        print("✅ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!")
        print("="*60)
        
        if webhook_url:
            print(f"\n🌐 Публичный URL: {webhook_url}")
        
        print("\n📋 Доступные команды в боте:")
        print("   /start - Начало и профиль")
        print("   /collection - Коллекция карт")
        print("   /expedition - Экспедиции (основной фарм)")
        print("   /daily - Ежедневные задания")
        print("   /arena - Арена PvP")
        print("   /open_pack - Открыть пачку")
        print("   /trade - Обмен картами")
        print("   /upgrade - Улучшить карту")
        print("   /dust - Распылить дубликат")
        
        print("\n🛠  Для разработчиков:")
        print("   http://localhost:8000/docs - API документация")
        print("   http://localhost:4040 - Ngrok интерфейс")
        
        print("\n🛑 Для остановки нажмите Ctrl+C дважды")
        print("="*60)
        
        # Держим процессы активными
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Получен сигнал остановки...")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка по запросу пользователя...")
    
    finally:
        # Останавливаем все процессы
        print("\n🔄 Остановка всех процессов...")
        
        # Ngrok
        if ngrok_process:
            ngrok_process.terminate()
            print("✅ Ngrok остановлен")
        
        # Остальные процессы
        for i, proc in enumerate(processes):
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"✅ Процесс {i+1} остановлен")
            except:
                try:
                    proc.kill()
                except:
                    pass
        
        print("\n✅ Все процессы остановлены. До свидания!")

if __name__ == "__main__":
    # Парсим аргументы командной строки
    use_webhook = "--webhook" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Использование: python scripts/dev.py [опции]")
        print("\nОпции:")
        print("  --webhook    Запуск с вебхуком (требует Ngrok)")
        print("  --polling    Запуск в polling режиме (по умолчанию)")
        print("  --help       Показать эту справку")
    else:
        start_development(use_webhook=use_webhook)