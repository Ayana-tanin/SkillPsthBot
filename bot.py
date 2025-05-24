import logging
import os
import asyncio
import signal
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импорт обработчиков
from handlers import commands, callbacks, messages, goals, materials, test, registration
from config import settings
from database import db, UserManager, TestProgressManager, TestResultsManager

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Регистрация обработчиков
def register_handlers(dispatcher):
    commands.register_handlers(dispatcher)
    callbacks.register_handlers(dispatcher)
    goals.register_handlers(dispatcher)
    materials.register_handlers(dispatcher)
    test.register_handlers(dispatcher)
    registration.register_registration_handlers(dispatcher)
    messages.register_handlers(dispatcher)


async def on_startup():
    """Действия при запуске бота"""
    try:
        # Подключение к базе данных
        await db.connect()
        logger.info("✅ База данных подключена")
        
        # Регистрация обработчиков
        register_handlers(dp)
        logger.info("✅ Обработчики зарегистрированы")
        
        # Удаление вебхука (если был установлен)
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Вебхук удален")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        raise


async def on_shutdown():
    """Действия при остановке бота"""
    try:
        # Закрытие соединения с базой данных
        await db.close()
        logger.info("✅ Соединение с базой данных закрыто")
        
        # Закрытие сессии бота
        await bot.session.close()
        logger.info("✅ Сессия бота закрыта")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при остановке: {e}")


async def main():
    """Основная функция запуска бота"""
    try:
        # Регистрация обработчиков сигналов
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(on_shutdown()))
        
        # Запуск бота
        await on_startup()
        logger.info("🚀 Бот запущен")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise
    finally:
        await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Необработанная ошибка: {e}")
        raise