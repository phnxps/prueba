import os
import psycopg2
from urllib.parse import urlparse

def get_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL no está definida")

    result = urlparse(db_url)
    return psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port,
        sslmode="require"
    )

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

def save_article(url):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO articles (url) VALUES (%s) ON CONFLICT (url) DO NOTHING', (url,))
                conn.commit()
    except Exception as e:
        print(f"Error al guardar artículo: {e}")

def is_article_saved(url):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT 1 FROM articles WHERE url = %s', (url,))
                return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error al comprobar artículo: {e}")
        return False

def delete_old_articles(days=30):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM articles WHERE created_at < NOW() - INTERVAL %s', (f'{days} days',))
            conn.commit()

def get_all_articles():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT url FROM articles')
            return [row[0] for row in cursor.fetchall()]
