import logging
import os
import asyncio
import subprocess
import sys
import time
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import threading

# Импорт обработчиков
from handlers import commands, callbacks, messages, goals, materials, test, registration
from config import settings

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Создаем отдельный логгер для FastAPI
fastapi_logger = logging.getLogger('fastapi')
fastapi_logger.setLevel(logging.INFO)
fastapi_handler = logging.StreamHandler()
fastapi_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
fastapi_logger.addHandler(fastapi_handler)

def wait_for_tables(cursor, expected_tables, max_retries=30, retry_interval=1):
    """Ожидание создания всех таблиц."""
    for i in range(max_retries):
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        missing_tables = set(expected_tables) - set(tables)
        
        if not missing_tables:
            logger.info(f"Все таблицы созданы: {', '.join(tables)}")
            return True
            
        logger.info(f"Ожидание создания таблиц... (попытка {i+1}/{max_retries})")
        logger.info(f"Ожидаемые таблицы: {', '.join(expected_tables)}")
        logger.info(f"Найденные таблицы: {', '.join(tables)}")
        logger.info(f"Отсутствующие таблицы: {', '.join(missing_tables)}")
        time.sleep(retry_interval)
    
    logger.error(f"Не все таблицы созданы за отведенное время. Ожидались: {', '.join(expected_tables)}")
    return False

def run_fastapi():
    """Запуск FastAPI в отдельном процессе."""
    try:
        logger.info("Запуск FastAPI приложения...")
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Вывод логов FastAPI через отдельный логгер
        def log_output(pipe, log_func):
            for line in pipe:
                if line.strip():
                    # Убираем префикс INFO: из логов FastAPI
                    line = line.replace("INFO:     ", "").strip()
                    log_func(line)
        
        threading.Thread(target=log_output, args=(process.stdout, fastapi_logger.info), daemon=True).start()
        threading.Thread(target=log_output, args=(process.stderr, fastapi_logger.error), daemon=True).start()
        
        return process
    except Exception as e:
        logger.error(f"Ошибка при запуске FastAPI: {e}")
        raise

# Инициализация бота и диспетчера
try:
    logger.info("Инициализация бота...")
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    logger.info("Бот успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка при инициализации бота: {e}")
    raise

# Регистрация обработчиков
def register_handlers(dispatcher):
    try:
        logger.info("Регистрация обработчиков...")
        commands.register_handlers(dispatcher)
        callbacks.register_handlers(dispatcher)
        goals.register_handlers(dispatcher)
        materials.register_handlers(dispatcher)
        test.register_handlers(dispatcher)
        registration.register_registration_handlers(dispatcher)
        messages.register_handlers(dispatcher)
        logger.info("Обработчики успешно зарегистрированы")
    except Exception as e:
        logger.error(f"Ошибка при регистрации обработчиков: {e}")
        raise

async def on_startup():
    try:
        logger.info("Запуск бота...")
        # Запускаем FastAPI
        api_process = run_fastapi()
        
        # Даем время на запуск FastAPI
        await asyncio.sleep(2)
        
        # Проверяем подключение к базе данных и создание таблиц
        try:
            from api.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            
            # Список ожидаемых таблиц
            expected_tables = ['users', 'test_results', 'test_progress', 'goals', 'materials', 'notes']
            
            # Ждем создания всех таблиц
            if not wait_for_tables(cursor, expected_tables):
                raise Exception("Не все таблицы были созданы")
                
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка при проверке базы данных: {e}")
            raise
            
        logger.info("Бот успешно запущен")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

async def on_shutdown():
    try:
        logger.info("Остановка бота...")
        # Закрытие соединений, очистка ресурсов и т.д.
        logger.info("Бот успешно остановлен")
    except Exception as e:
        logger.error(f"Ошибка при остановке бота: {e}")
        raise

async def main():
    try:
        # Регистрация обработчиков
        register_handlers(dp)

        # Установка хэндлеров для запуска и завершения
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        # Запуск бота
        logger.info("Начало работы бота...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критическая ошибка в main: {e}")
        raise

if __name__ == '__main__':
    try:
        logger.info("Запуск приложения...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения работы")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}")
        raise