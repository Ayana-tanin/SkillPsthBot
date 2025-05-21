import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Используем переменную окружения MYSQL_URL, если она задана, иначе берём отдельные параметры из Railway.
    mysql_url = os.getenv("MYSQL_URL")
    if mysql_url:
         # Пример: mysql_url = "mysql://root:password@host:port/database"
         # (в Railway MYSQL_URL уже содержит все параметры)
         try:
             connection = mysql.connector.connect(host=mysql_url.split("@")[1].split("/")[0].split(":")[0], user=mysql_url.split("://")[1].split(":")[0], password=mysql_url.split("://")[1].split(":")[1].split("@")[0], database=mysql_url.split("/")[-1], port=int(mysql_url.split("@")[1].split("/")[0].split(":")[1] if ":" in mysql_url.split("@")[1].split("/")[0] else "3306"))
             return connection
         except mysql.connector.Error as err:
             print(f"Ошибка подключения к базе данных (MYSQL_URL): {err}")
             raise
    else:
         # Если MYSQL_URL не задан, используем отдельные переменные окружения Railway.
         host = os.getenv("RAILWAY_PRIVATE_DOMAIN", os.getenv("MYSQLHOST", "localhost"))
         user = os.getenv("MYSQLUSER", "root")
         password = os.getenv("MYSQL_ROOT_PASSWORD", os.getenv("MYSQLPASSWORD", ""))
         database = os.getenv("MYSQL_DATABASE", os.getenv("MYSQLDATABASE", "railway"))
         port = int(os.getenv("RAILWAY_TCP_PROXY_PORT", os.getenv("MYSQLPORT", "3306")))
         try:
             connection = mysql.connector.connect(host=host, user=user, password=password, database=database, port=port)
             return connection
         except mysql.connector.Error as err:
             print(f"Ошибка подключения к базе данных (отдельные параметры): {err}")
             raise