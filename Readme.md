# PlayStation Bot (Telegram)

Este bot notifica automáticamente por Telegram cuando se publican nuevos juegos en esta categoría de la PS Store:

https://store.playstation.com/es-es/category/3bf499d7-7acf-4931-97dd-2667494ee2c9

## Configuración

1. Crea un bot con @BotFather y obtén el `TELEGRAM_TOKEN`.
2. Obtén tu `CHAT_ID` desde `getUpdates` tras enviar un mensaje al bot.
3. Crea un archivo `config.py` como este:

```python
TELEGRAM_TOKEN = 'TU_TOKEN'
CHAT_ID = 'TU_CHAT_ID'
