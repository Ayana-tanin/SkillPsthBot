import logging
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импорт обработчиков
from handlers import commands, callbacks, messages, goals, materials, test, registration
from config import settings

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Изменено на DEBUG для более подробного логирования
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[ logging.StreamHandler() ]  # Вывод только в консоль (удалён FileHandler)
)
logger = logging.getLogger(__name__)

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
        # Проверяем подключение к базе данных
        try:
            from api.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logger.info(f"Подключение к базе данных успешно. Найдены таблицы: {[table[0] for table in tables]}")
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