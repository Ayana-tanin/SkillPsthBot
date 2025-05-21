import mysql.connector
import os

# Подключаемся к серверу MySQL (без указания базы, чтобы создать её)
conn = mysql.connector.connect(
    host="mysql.railway.internal",
    user="root",
    password="uHxkEoEUEHzOXtakRuPFKikhvjXSxrNk",
    port=3306,
    database="railway"
)
conn.autocommit = True
cursor = conn.cursor()

# Создаем базу, если не существует
cursor.execute("CREATE DATABASE IF NOT EXISTS skillpath")
cursor.execute("USE skillpath")

# Создаем таблицы
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id VARCHAR(100),
    fio VARCHAR(255),
    school VARCHAR(255),
    class_number INT,
    class_letter VARCHAR(10),
    gender VARCHAR(20),
    birth_year INT,
    city VARCHAR(100),
    language VARCHAR(50),
    artifacts TEXT,
    opened_profiles TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS test_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id VARCHAR(100),
    current_scene VARCHAR(100),
    all_scenes TEXT,
    profile_scores TEXT,
    profession_scores TEXT,
    lang VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS test_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id VARCHAR(100),
    finished_at TIMESTAMP,
    profile VARCHAR(100),
    score INT,
    details TEXT
);
""")

# Добавляем внешние ключи (если их нет)
try:
    cursor.execute("""
    ALTER TABLE test_progress
        ADD CONSTRAINT fk_test_progress_user
        FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
    """)
except mysql.connector.Error as e:
    if e.errno == 1826:  # Duplicate foreign key name
        pass
    else:
        raise

try:
    cursor.execute("""
    ALTER TABLE test_results
        ADD CONSTRAINT fk_test_results_user
        FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
    """)
except mysql.connector.Error as e:
    if e.errno == 1826:
        pass
    else:
        raise

cursor.close()
conn.close()
print("База и таблицы созданы (если их не было)")
