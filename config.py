import os
from pydantic_settings import BaseSettings  # type: ignore
from dotenv import load_dotenv
import json

load_dotenv()

class Settings(BaseSettings):
    """Настройки приложения."""
    # Основные настройки
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", 0))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Настройки Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    
    # Настройки MySQL (Railway)
    MYSQL_HOST: str = os.getenv("RAILWAY_PRIVATE_DOMAIN", os.getenv("MYSQLHOST", "localhost"))
    MYSQL_USER: str = os.getenv("MYSQLUSER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_ROOT_PASSWORD", os.getenv("MYSQLPASSWORD", ""))
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", os.getenv("MYSQLDATABASE", "railway"))
    MYSQL_PORT: int = int(os.getenv("RAILWAY_TCP_PROXY_PORT", os.getenv("MYSQLPORT", "3306")))
    
    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    
    # Список администраторов (строка, парсится вручную)
    ADMIN_IDS: str = os.getenv("ADMIN_IDS", "")
    
    # Настройки API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", "8000"))  # Используем PORT из Railway
    API_URL: str = os.getenv("API_URL", f"http://localhost:{API_PORT}")  # Всегда используем localhost для внутренних запросов
    
    class Config:
        env_file = ".env"
        extra = 'allow'
        case_sensitive = True

    @property
    def admin_ids(self) -> list[int]:
        value = self.ADMIN_IDS.strip()
        if not value:
            return []
        # Пробуем как json
        try:
            ids = json.loads(value)
            if isinstance(ids, list):
                return [int(x) for x in ids]
        except Exception:
            pass
        # Иначе парсим через запятую
        return [int(x) for x in value.split(',') if x.strip().isdigit()]

    @property
    def mysql_url(self) -> str:
        """Получить URL подключения к MySQL в формате Railway."""
        return f"mysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

settings = Settings()

if not settings.BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения") 