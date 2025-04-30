import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time
import os
from flask import Flask
from threading import Thread

# Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Configuración inicial
URL = 'https://store.playstation.com/es-es/category/3bf499d7-7acf-4931-97dd-2667494ee2c9'
bot = Bot(token=TELEGRAM_TOKEN)
notificados = []

# Mensaje de arranque
bot.send_message(chat_id=CHAT_ID, text="✅ Bot de PS Store iniciado en Railway")

def obtener_juegos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    juegos = soup.find_all('span', class_='psw-t-title-m')
    return [j.get_text(strip=True) for j in juegos]

def verificar_nuevos_juegos():
    global notificados
    while True:
        try:
            juegos_actuales = obtener_juegos()
            nuevos = [j for j in juegos_actuales if j not in notificados]
            for juego in nuevos:
                bot.send_message(chat_id=CHAT_ID, text=f"🆕 Nuevo juego: {juego}")
                notificados.append(juego)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"❌ Error: {e}")
        time.sleep(1200)  # cada 20 minutos

# Servidor web para mantener Railway activo
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot corriendo en Railway"

if __name__ == "__main__":
    # Inicia el bot en un hilo separado
    Thread(target=verificar_nuevos_juegos).start()
    # Inicia el servidor Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
