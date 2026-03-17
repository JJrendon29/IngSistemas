import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST'),
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
    'database': os.environ.get('MYSQL_DB'),
    'port': int(os.environ.get('MYSQL_PORT')),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except pymysql.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None