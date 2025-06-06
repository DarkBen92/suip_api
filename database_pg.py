import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "parsepdfdb")


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def save_metadata(metadata: dict) -> int:
    """Сохранение метаданных в базу данных.
    
    :param metadata: Словарь с метаданными
    :return: ID сохраненной записи
    """
    query = '''
    INSERT INTO pdf_metadata (
        filename, catalog, size_file, date_edited_file, date_access_file, date_update_index_file,
        resolution_file, extension_file, filetype, mime_type, version_file, page_count,
        creator, producer, date_digitization
    ) VALUES (
        %(filename)s, %(catalog)s, %(size_file)s, %(date_edited_file)s, %(date_access_file)s, %(date_update_index_file)s,
        %(resolution_file)s, %(extension_file)s, %(filetype)s, %(mime_type)s, %(version_file)s, %(page_count)s,
        %(creator)s, %(producer)s, %(date_digitization)s
    ) RETURNING id;
    '''
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, metadata)
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id


def get_all_metadata():
    """Получение всех метаданных из базы данных.
    
    :return: Список словарей с метаданными
    """
    query = '''
    SELECT id, filename, catalog, size_file, date_edited_file, date_access_file, 
           date_update_index_file, resolution_file, extension_file, filetype, 
           mime_type, version_file, page_count, creator, producer, date_digitization
    FROM pdf_metadata
    ORDER BY created_at DESC;
    '''
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            results = []
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))
            return results
