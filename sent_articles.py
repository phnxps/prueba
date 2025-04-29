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

# Resto de funciones que usan get_connection()
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

# etc.