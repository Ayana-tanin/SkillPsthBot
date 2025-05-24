import logging
import os
import asyncio
import signal
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from database import db, UserManager, TestProgressManager, TestResultsManager

# Импорт обработчиков
from handlers import commands, callbacks, messages, goals, materials, test, registration
from config import settings

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
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Flag to track if shutdown is in progress
is_shutting_down = False

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
    global is_shutting_down
    if is_shutting_down:
        return
    
    is_shutting_down = True
    logger.info("Shutting down bot...")
    
    try:
        # Закрытие соединения с базой данных
        await db.close()
        logger.info("✅ Соединение с базой данных закрыто")
        
        # Закрытие сессии бота
        await bot.session.close()
        logger.info("✅ Сессия бота закрыта")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при остановке: {e}")


def handle_signal(signum, frame):
    """Handle system signals for graceful shutdown"""
    logger.info(f"Received signal {signum}")
    asyncio.create_task(on_shutdown())


async def main():
    """Основная функция запуска бота"""
    try:
        # Регистрация обработчиков сигналов
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, handle_signal)
        
        # Запуск бота
        await on_startup()
        logger.info("🚀 Бот запущен")
        
        # Set up startup and shutdown handlers
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Запуск бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise
    finally:
        if not is_shutting_down:
            await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Необработанная ошибка: {e}")
        raise