import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "parsepdfdb")


def create_database():
    """Создает базу данных, если она не существует."""
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            exists = cur.fetchone()
            
            if not exists:
                print(f"Создание базы данных {DB_NAME}...")
                cur.execute(f"CREATE DATABASE {DB_NAME}")
                print(f"База данных {DB_NAME} успешно создана!")
            else:
                print(f"База данных {DB_NAME} уже существует.")
    finally:
        conn.close()


def create_table():
    """Создает таблицу pdf_metadata."""
    query = '''
    CREATE TABLE IF NOT EXISTS pdf_metadata (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        catalog VARCHAR(255),
        size_file VARCHAR(100),
        date_edited_file VARCHAR(100),
        date_access_file VARCHAR(100),
        date_update_index_file VARCHAR(100),
        resolution_file VARCHAR(100),
        extension_file VARCHAR(50),
        filetype VARCHAR(50),
        mime_type VARCHAR(100),
        version_file VARCHAR(50),
        page_count VARCHAR(50),
        creator VARCHAR(255),
        producer VARCHAR(255),
        date_digitization VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    try:
        with conn.cursor() as cur:
            print("Создание таблицы pdf_metadata...")
            cur.execute(query)
            conn.commit()
            print("Таблица pdf_metadata успешно создана!")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Начало инициализации базы данных...")
    create_database()
    create_table()
    print("Инициализация базы данных завершена успешно!") 
    