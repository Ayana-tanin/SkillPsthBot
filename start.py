import os
import sys
import time
import logging
import subprocess
import requests
from api.db import init_database

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def wait_for_api(port, max_retries=30, retry_interval=1):
    """Ожидание готовности API."""
    api_url = f"http://localhost:{port}/users/"
    for i in range(max_retries):
        try:
            response = requests.get(api_url + "?telegram_id=1")
            if response.status_code == 200:
                logger.info("API успешно запущен и отвечает")
                return True
        except requests.exceptions.ConnectionError:
            logger.info(f"Ожидание запуска API... (попытка {i+1}/{max_retries})")
            time.sleep(retry_interval)
    logger.error("API не запустился за отведенное время")
    return False

def main():
    try:
        # Получаем порт из переменной окружения или используем 8000
        port = os.getenv("PORT", "8000")
        
        # Запускаем FastAPI в отдельном процессе
        logger.info("Запуск FastAPI приложения...")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", port],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Ждем запуска API
        if not wait_for_api(port):
            logger.error("Не удалось дождаться запуска API")
            api_process.terminate()
            sys.exit(1)
        
        # Запускаем бота
        logger.info("Запуск бота...")
        bot_process = subprocess.Popen(
            [sys.executable, "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Ждем завершения процессов
        api_process.wait()
        bot_process.wait()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
        if 'api_process' in locals():
            api_process.terminate()
        if 'bot_process' in locals():
            bot_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main() 