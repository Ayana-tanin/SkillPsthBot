import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Получаем значения из переменных окружения Railway
    host = os.getenv("RAILWAY_PRIVATE_DOMAIN", os.getenv("MYSQLHOST", "localhost"))
    user = os.getenv("MYSQLUSER", "root")
    password = os.getenv("MYSQL_ROOT_PASSWORD", os.getenv("MYSQLPASSWORD", ""))
    database = os.getenv("MYSQL_DATABASE", os.getenv("MYSQLDATABASE", "railway"))
    port = int(os.getenv("RAILWAY_TCP_PROXY_PORT", os.getenv("MYSQLPORT", "3306")))

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Ошибка подключения к базе данных: {err}")
        raise