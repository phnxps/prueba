from dotenv import load_dotenv
import os
import psycopg2

# Cargar variables de entorno
load_dotenv()

# Variables de conexión
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Función para conectarse a la base de datos
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'  # IMPORTANTE para Supabase
    )

# Inicializar la tabla si no existe
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

# Guardar un artículo
def save_article(url):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO articles (url) VALUES (%s) ON CONFLICT (url) DO NOTHING', (url,))
                conn.commit()
    except Exception as e:
        print(f"Error al guardar artículo: {e}")

# Comprobar si un artículo ya está guardado
def is_article_saved(url):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT 1 FROM articles WHERE url = %s', (url,))
                result = cursor.fetchone()
                return result is not None
    except Exception as e:
        print(f"Error comprobando si artículo está guardado: {e}")
        return False

# Obtener todos los artículos guardados
def get_all_articles():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT url FROM articles')
                articles = [row[0] for row in cursor.fetchall()]
                return articles
    except Exception as e:
        print(f"Error obteniendo artículos: {e}")
        return []

# Eliminar artículos antiguos
def delete_old_articles(days=30):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM articles WHERE created_at < NOW() - INTERVAL %s', (f'{days} days',))
                conn.commit()
    except Exception as e:
        print(f"Error eliminando artículos antiguos: {e}")
