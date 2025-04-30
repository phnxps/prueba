import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time
import os

# Variables de entorno (configura en Railway)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

URL = 'https://store.playstation.com/es-es/category/3bf499d7-7acf-4931-97dd-2667494ee2c9'
bot = Bot(token=TELEGRAM_TOKEN)
notificados = []

def obtener_juegos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    juegos = soup.find_all('span', class_='psw-t-title-m')
    return [j.get_text(strip=True) for j in juegos]

def verificar_nuevos_juegos():
    global notificados
    juegos_actuales = obtener_juegos()
    nuevos = [j for j in juegos_actuales if j not in notificados]
    for juego in nuevos:
        bot.send_message(chat_id=CHAT_ID, text=f"🆕 Nuevo juego: {juego}")
        notificados.append(juego)

if __name__ == "__main__":
    while True:
        verificar_nuevos_juegos()
        time.sleep(21600)  # cada 6h
