import mysql.connector
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def check_database_exists(cursor, database_name):
    """Проверка существования базы данных."""
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall()]
    return database_name in databases

def check_table_exists(cursor, table_name):
    """Проверка существования таблицы."""
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    return table_name in tables

def init_database():
    """Инициализация базы данных - проверка и создание таблиц в существующей БД."""
    # Подключаемся к существующей базе данных из MYSQL_URL
    mysql_url = os.getenv("MYSQL_URL")
    if not mysql_url:
        logger.error("MYSQL_URL не установлен в переменных окружения")
        raise ValueError("MYSQL_URL не установлен в переменных окружения")
    
    logger.info(f"Начинаем инициализацию базы данных с URL: {mysql_url}")
    
    try:
        # Подключаемся к существующей базе данных
        connection = mysql.connector.connect(
            host=mysql_url.split("@")[1].split("/")[0].split(":")[0],
            user=mysql_url.split("://")[1].split(":")[0],
            password=mysql_url.split("://")[1].split(":")[1].split("@")[0],
            database=mysql_url.split("/")[-1],
            port=int(mysql_url.split("@")[1].split("/")[0].split(":")[1] if ":" in mysql_url.split("@")[1].split("/")[0] else "3306")
        )
        logger.info(f"Успешное подключение к базе данных {mysql_url.split('/')[-1]}")
    except mysql.connector.Error as err:
        logger.error(f"Ошибка подключения к базе данных: {err}")
        raise

    cursor = connection.cursor()
    try:
        # Проверяем существование таблиц
        tables_to_check = ['users', 'test_results', 'test_progress']
        logger.info(f"Проверяем существование таблиц: {', '.join(tables_to_check)}")
        
        existing_tables = [table for table in tables_to_check if check_table_exists(cursor, table)]
        logger.info(f"Найдены существующие таблицы: {', '.join(existing_tables) if existing_tables else 'нет'}")
        
        if not existing_tables:
            logger.info("Таблицы не существуют. Создаем все таблицы...")
        else:
            missing_tables = [table for table in tables_to_check if table not in existing_tables]
            if missing_tables:
                logger.info(f"Создаем отсутствующие таблицы: {', '.join(missing_tables)}")

        # Создание таблицы users, если её нет
        if 'users' not in existing_tables:
            logger.info("Создаем таблицу users...")
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNSIGNED UNIQUE,
                    fio VARCHAR(255),
                    school VARCHAR(255),
                    class_number INT,
                    class_letter VARCHAR(10),
                    gender VARCHAR(10),
                    birth_year INT,
                    city VARCHAR(255),
                    language VARCHAR(20),
                    artifacts TEXT,
                    opened_profiles TEXT
                )
            """)
            logger.info("Таблица users успешно создана")
        
        # Создание таблицы test_results, если её нет
        if 'test_results' not in existing_tables:
            logger.info("Создаем таблицу test_results...")
            cursor.execute("""
                CREATE TABLE test_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNSIGNED,
                    finished_at DATETIME,
                    profile VARCHAR(255),
                    score INT,
                    details TEXT
                )
            """)
            logger.info("Таблица test_results успешно создана")
        
        # Создание таблицы test_progress, если её нет
        if 'test_progress' not in existing_tables:
            logger.info("Создаем таблицу test_progress...")
            cursor.execute("""
                CREATE TABLE test_progress (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNSIGNED,
                    current_scene INT,
                    all_scenes TEXT,
                    profile_scores TEXT,
                    profession_scores TEXT,
                    lang VARCHAR(10),
                    updated_at DATETIME
                )
            """)
            logger.info("Таблица test_progress успешно создана")
        
        connection.commit()
        logger.info("Инициализация таблиц завершена успешно")
    except mysql.connector.Error as err:
        logger.error(f"Ошибка при создании таблиц: {err}")
        raise
    finally:
        cursor.close()
        connection.close()
        logger.info("Соединение с базой данных закрыто")

def get_connection():
    # Используем переменную окружения MYSQL_URL
    mysql_url = os.getenv("MYSQL_URL")
    if not mysql_url:
        raise ValueError("MYSQL_URL не установлен в переменных окружения")
    
    try:
        connection = mysql.connector.connect(
            host=mysql_url.split("@")[1].split("/")[0].split(":")[0],
            user=mysql_url.split("://")[1].split(":")[0],
            password=mysql_url.split("://")[1].split(":")[1].split("@")[0],
            database=mysql_url.split("/")[-1],
            port=int(mysql_url.split("@")[1].split("/")[0].split(":")[1] if ":" in mysql_url.split("@")[1].split("/")[0] else "3306")
        )
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Ошибка подключения к базе данных: {err}")
        raise