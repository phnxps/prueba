import os
import psycopg2

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
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
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM articles WHERE url = %s', (url,))
            result = cursor.fetchone()
            return result is not None

def delete_old_articles(days=30):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM articles WHERE created_at < NOW() - INTERVAL %s', (f'{days} days',))
            conn.commit()

def get_all_articles():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT url FROM articles')
            articles = [row[0] for row in cursor.fetchall()]
            return articles

if __name__ == "__main__":
    init_db()
    save_article("https://ejemplo.com/test")
    print("✅ Guardado de prueba ejecutado.")