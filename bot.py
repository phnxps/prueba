import requests
from bs4 import BeautifulSoup
from telegram import Bot
from config import TELEGRAM_TOKEN, CHAT_ID
import time

# URL de la categoría PS Store
URL = 'https://store.playstation.com/es-es/category/3bf499d7-7acf-4931-97dd-2667494ee2c9'

# Inicializa el bot
bot = Bot(token=TELEGRAM_TOKEN)

# Guarda juegos ya notificados
notificados = []

def obtener_juegos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    juegos = soup.find_all('span', class_='psw-t-title-m')
    titulos = [j.get_text(strip=True) for j in juegos]
    return titulos

def verificar_nuevos_juegos():
    global notificados
    juegos_actuales = obtener_juegos()
    nuevos = [j for j in juegos_actuales if j not in notificados]

    for juego in nuevos:
        mensaje = f"🆕 Nuevo juego en la PS Store: {juego}"
        bot.send_message(chat_id=CHAT_ID, text=mensaje)
        notificados.append(juego)

if __name__ == "__main__":
    while True:
        verificar_nuevos_juegos()
        time.sleep(3600 * 6)  # cada 6 horas
