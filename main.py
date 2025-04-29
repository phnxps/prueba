from sent_articles import init_db, save_article, is_article_saved
init_db()
import os
import feedparser
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder
from datetime import datetime, timedelta
import random
import requests
from bs4 import BeautifulSoup
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

init_db()

RSS_FEEDS = [
    'https://vandal.elespanol.com/rss/',
    'https://www.3djuegos.com/rss/',
    'https://www.hobbyconsolas.com/categoria/novedades/rss',
    'https://www.vidaextra.com/feed',
    'https://www.nintenderos.com/feed',
    'https://as.com/meristation/portada/rss.xml',
    'https://blog.es.playstation.com/feed/',
    'https://www.nintendo.com/es/news/rss.xml',
    'https://news.xbox.com/es-mx/feed/',
    'https://nintenduo.com/category/noticias/feed/',
    'https://www.xataka.com/tag/nintendo/rss',
    'https://www.xataka.com/tag/playstation/rss',
    'https://www.laps4.com/feed/',
    'https://areajugones.sport.es/feed/',
]

CURIOSIDADES = [
    "La PlayStation nació tras un fallo con Nintendo. 🎮",
    "El primer easter egg fue en Adventure (1979). 🚀",
    "Mario se iba a llamar 'Jumpman'. 🍄",
    "GTA V es el producto más rentable del entretenimiento. 💰",
    "La Nintendo 64 introdujo el primer joystick analógico. 🎮",
    "La Switch es la consola híbrida más vendida de la historia. 🔥",
    "La PlayStation 2 es la consola más vendida de todos los tiempos. 🥇",
    "En Japón, 'Kirby' es visto como un símbolo de felicidad. 🌟",
    "Zelda: Breath of the Wild reinventó los mundos abiertos. 🧭",
    "La primera consola portátil fue la Game Boy (1989). 📺",
    "Halo fue pensado originalmente como un juego de estrategia en tiempo real. ⚔️",
    "La saga Pokémon es la franquicia más rentable del mundo. 🧢",
    "Crash Bandicoot fue desarrollado para rivalizar contra Mario. 🏁",
    "El primer videojuego de la historia es considerado 'Tennis for Two' de 1958. 🎾",
    "El control de la Xbox original se apodaba 'The Duke' por su tamaño. 🎮",
    "Metroid fue uno de los primeros juegos en presentar una protagonista femenina. 🚀",
    "Sega dejó de fabricar consolas tras el fracaso de Dreamcast. 🌀",
    "La consola Wii de Nintendo se llamaba inicialmente 'Revolution'. 🔥",
    "PlayStation 5 agotó su stock en Amazon en menos de 12 segundos. ⚡",
    "Breath of the Wild fue lanzado junto a la Nintendo Switch y redefinió los mundos abiertos. 🌎",
    "GTA V recaudó más de 800 millones de dólares en su primer día. 💵",
    "The Last of Us Part II ganó más de 300 premios de Juego del Año. 🏆",
    "Red Dead Redemption 2 tardó 8 años en desarrollarse. 🐎",
    "Cyberpunk 2077 vendió 13 millones de copias en sus primeras tres semanas. 🤖",
    "Animal Crossing: New Horizons fue el fenómeno social de 2020. 🏝️",
    "Call of Duty: Modern Warfare 3 fue el juego más vendido de 2011. 🎯",
    "El primer tráiler de Elden Ring tardó 2 años en publicarse tras su anuncio. 🕯️",
]



proximos_lanzamientos = []
last_curiosity_sent = datetime.now() - timedelta(hours=6)

async def send_news(context, entry):
    if hasattr(entry, 'published_parsed'):
        published = datetime(*entry.published_parsed[:6])
        forced_today = datetime(2025, 4, 29).date()
        if published.date() != forced_today:
            return

    # Filtro mejorado: sólo noticias relevantes de videojuegos
    valid_keywords = [
        "videojuego", "videojuegos", "juego", "juegos", "playstation", "ps5", "ps4",
        "xbox", "series x", "series s", "nintendo", "switch", "consola", "gameplay",
        "tráiler", "trailer", "beta", "demo", "expansion", "dlc", "actualización",
        "remaster", "remake", "multijugador", "early access", "open beta", "requisitos",
        "jugable", "filtrado", "filtrada", "leak", "desarrollo", "anuncio", "anunciado"
    ]
    blocked_keywords = [
        "teclado", "hardware", "ratón gaming", "ratón", "periférico", "gaming gear",
        "iphone", "ipad", "android", "smartphone", "smartwatch",
        "película", "películas", "serie", "series", "netflix", "disney+",
        "hbo", "filme", "cine", "manga", "anime", "cómic", "comics",
        "oferta teclado", "oferta ratón", "rebaja gaming gear"
    ]
    title_summary = (entry.title + " " + (entry.summary if hasattr(entry, 'summary') else "")).lower()

    contiene_valida = any(p in title_summary for p in valid_keywords)
    contiene_bloqueada = any(p in title_summary for p in blocked_keywords)

    # Excepción: permitir franquicias aunque haya palabras bloqueadas
    franquicias_permitidas = [
        "pokemon masters", "overwatch", "zelda", "titanfall", "gears of war", "halo",
        "call of duty", "final fantasy", "resident evil", "assassin's creed"
    ]
    if any(franq in title_summary for franq in franquicias_permitidas):
        contiene_bloqueada = False

    # Nueva lógica mejorada
    es_oferta_juego_o_consola = any(p in title_summary for p in [
        "juego", "videojuego", "consola", "ps5", "ps4", "xbox", "switch", 
        "dualshock", "dual sense", "pro controller", "joy-con", "headset ps5", "auriculares xbox"
    ]) and any(p in title_summary for p in [
        "oferta", "rebaja", "descuento", "promoción", "precio especial", "chollo", "ahorro"
    ])

    if contiene_bloqueada:
        print(f"🔴 Descartada por palabra bloqueada → {entry.title}")
        return

    if not contiene_valida and not es_oferta_juego_o_consola:
        print(f"🔴 Descartada por no ser de videojuegos → {entry.title}")
        return

    # Filtro estricto: sólo pasar si claramente se menciona videojuego
    if not any(word in title_summary for word in [
        "juego", "videojuego", "consola", "nintendo", "playstation", "xbox", 
        "ps5", "ps4", "switch", "steam", "gameplay", "tráiler", "trailer", 
        "expansión", "dlc", "beta", "demo", "remaster", "remake", "early access", "battle pass"
    ]):
        print(f"🔴 Descartada: noticia no relacionada con videojuegos → {entry.title}")
        return

    # Filtro: excluir noticias de cine o series que no estén relacionadas con videojuegos
    title_lower = entry.title.lower()
    summary_lower = (entry.summary if hasattr(entry, 'summary') else "").lower()

    if any(keyword in title_lower for keyword in ["película", "serie", "actor", "cine", "temporada", "episodio"]) and not any(
        related in title_lower for related in ["juego", "videojuego", "expansión", "dlc", "adaptación", "game"]
    ):
        return

    if any(keyword in summary_lower for keyword in ["película", "serie", "actor", "cine", "temporada", "episodio"]) and not any(
        related in summary_lower for related in ["juego", "videojuego", "expansión", "dlc", "adaptación", "game"]
    ):
        return

    link = entry.link.lower()
    if 'playstation' in link:
        platform_label = 'PLAYSTATION'
        icon = '🎮'
        tag = '#PlayStation'
    elif 'switch 2' in link or 'switch-2' in link:
        platform_label = 'NINTENDO SWITCH 2'
        icon = '🍄'
        tag = '#NintendoSwitch2'
    elif 'switch' in link:
        platform_label = 'NINTENDO SWITCH'
        icon = '🍄'
        tag = '#NintendoSwitch'
    elif 'xbox' in link:
        platform_label = 'XBOX'
        icon = '🟢'
        tag = '#Xbox'
    else:
        platform_label = 'NOTICIAS GAMER'
        icon = '🎮'
        tag = '#NoticiasGamer'

    # Ajuste de plataforma en base a etiquetas especiales prioritarias
    # Prioridad: Evento > Oferta > Guía > Análisis
    if any(tag == "#EventoEspecial" for tag in special_tags):
        platform_label = 'EVENTO ESPECIAL'
        icon = '🎬'
    elif any(tag == "#OfertaGamer" for tag in special_tags):
        platform_label = 'OFERTA GAMER'
        icon = '💸'
    elif any(tag == "#GuiaGamer" for tag in special_tags):
        platform_label = 'GUIA GAMER'
        icon = '📚'
    elif any(tag == "#ReviewGamer" for tag in special_tags):
        platform_label = 'ANÁLISIS GAMER'
        icon = '📝'

    title_lower = entry.title.lower()

    link_lower = entry.link.lower()

    # Detección de análisis de Laps4 como ReviewGamer
    if "laps4.com" in link_lower and "análisis" in title_lower:
        special_tags.append("#ReviewGamer")
        emoji_special = '📝'

    special_tags = []
    emoji_special = ''

    # Evento especial detection
    evento_keywords = [
        "state of play", "nintendo direct", "showcase", "summer game fest",
        "game awards", "evento especial", "presentation", "conference", "presentación",
        "wholesome direct", "evento de juegos", "evento indie", "presentación indie"
    ]

    if any(kw in title_lower for kw in evento_keywords):
        special_tags.insert(0, "#EventoEspecial")
        emoji_special = '🎬'

    # Trailer detection
    if any(kw in title_lower for kw in ["tráiler", "trailer", "avance", "gameplay"]):
        special_tags.append("#TrailerOficial")
        if not emoji_special:
            emoji_special = '🔥'

    # Free game detection
    if any(kw in title_lower for kw in ["gratis", "free", "regalo"]):
        special_tags.append("#JuegoGratis")
        if not emoji_special:
            emoji_special = '🎁'

    # Proximo lanzamiento detection
    if any(kw in title_lower for kw in ["anunci", "lanzamiento", "próximo", "proximo", "sale", "disponible", "estrena", "estreno", "estrenará", "fecha confirmada", "open beta", "demo", "early access", "llegará", "fecha de salida", "confirmado para", "a la venta"]):
        if not any(block in title_lower for block in ["mantenimiento", "servidores", "online", "downtime", "actualización", "patch notes"]):
            special_tags.append("#ProximoLanzamiento")
            if not emoji_special:
                emoji_special = '🎉'

    # Oferta especial detection (mejorado: incluye reservas y más expresiones)
    if any(kw in title_lower for kw in [
        "oferta", "rebaja", "descuento", "promoción", "precio especial", 
        "baja de precio", "chollo", "ahorro", "por menos de", "por solo", 
        "cuesta solo", "ahora a", "costaba", "a este precio", "reservar", "reserva", "mejor precio", "disponible para reservar"
    ]):
        special_tags.append("#OfertaGamer")
        if not emoji_special:
            emoji_special = '💸'

    # Guia Gamer detection (después de #OfertaGamer)
    if any(kw in title_lower for kw in [
        "guía", "trucos", "cómo", "dónde", "localización", "encontrar", 
        "conseguir", "desbloquear", "todos los secretos", "cómo encontrar", "guia completa"
    ]):
        special_tags.append("#GuiaGamer")

    if "#ProximoLanzamiento" in special_tags:
        fecha_publicacion = published.strftime('%d/%m/%Y') if 'published' in locals() else "Próximamente"
        proximos_lanzamientos.append(f"- {entry.title} ({fecha_publicacion})")

    # Review detection
    if any(kw in title_lower for kw in ["análisis", "review", "reseña", "comparativa"]):
        special_tags.append("#ReviewGamer")

    photo_url = None
    if entry.get("media_content"):
        for m in entry.media_content:
            if m.get("type", "").startswith("image/"):
                photo_url = m.get("url")
                break
    if not photo_url and entry.get("enclosures"):
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                photo_url = enc.get("url")
                break

    if not photo_url:
        try:
            r = requests.get(entry.link, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                photo_url = og_image.get('content')
        except Exception as e:
            print(f"Error obteniendo imagen por scraping: {e}")

    hashtags = " ".join(special_tags + [tag])

    caption = (
        f"{icon} *{platform_label}*\n\n"
        f"{emoji_special} *{entry.title}*\n\n"
        f"{hashtags}"
    ).strip()

    button = InlineKeyboardMarkup([[InlineKeyboardButton("📰 Leer noticia completa", url=entry.link)]])

    try:
        if photo_url:
            await context.bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=photo_url,
                caption=caption,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                reply_markup=button
            )
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=caption,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                disable_web_page_preview=False,
                reply_markup=button
            )
    except Exception as e:
        print(f"Error al enviar noticia: {e}")

async def send_curiosity(context):
    curiosity = random.choice(CURIOSIDADES)
    message = f"🕹️ *Curiosidad Gamer*\n{curiosity}\n\n#Gamepulse360 #DatoGamer"
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=message,
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )
    except Exception as e:
        print(f"Error al enviar curiosidad: {e}")

async def check_feeds(context):
    global last_curiosity_sent
    new_article_sent = False

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            if is_article_saved(entry.link):
                print(f"🔴 Descartada: link ya enviado anteriormente → {entry.link}")
                continue

            if hasattr(entry, 'published_parsed'):
                published = datetime(*entry.published_parsed[:6])
                if datetime.now() - published > timedelta(hours=6):
                    print(f"🔴 Descartada: demasiado antigua ({published}) → {entry.link}")
                    continue

            await send_news(context, entry)
            print(f"✅ Publicada correctamente: {entry.title}")
            save_article(entry.link)
            new_article_sent = True

    # Revisión de eventos especiales detectados hoy
    today = datetime.now().date()
    from sent_articles import get_all_articles  # Necesitamos tener esta función en sent_articles.py
    articles_today = [link for link in get_all_articles() if datetime.now().date() == today]

    eventos_detectados = False
    for article in articles_today:
        if any(keyword in article.lower() for keyword in ["state of play", "nintendo direct", "showcase", "summer game fest", "game awards", "evento especial", "presentation", "conference", "presentación"]):
            eventos_detectados = True
            break

    if eventos_detectados:
        try:
            evento_texto = "🎬 *¡Hoy hay eventos especiales en el mundo gamer!*\n\nPrepárate para seguir todas las novedades. 👾🔥"
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=evento_texto,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
        except Exception as e:
            print(f"Error al enviar mensaje de eventos especiales: {e}")

    if not new_article_sent:
        if datetime.now().weekday() == 6:  # Domingo
            await send_launch_summary(context)
        now = datetime.now()
        if now - last_curiosity_sent > timedelta(hours=6):
            await send_curiosity(context)
            last_curiosity_sent = now

async def send_launch_summary(context):
    if not proximos_lanzamientos:
        return
    resumen = "🚀 *Próximos lanzamientos detectados:*\n\n" + "\n".join(proximos_lanzamientos)
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=resumen,
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )
        proximos_lanzamientos.clear()
    except Exception as e:
        print(f"Error al enviar resumen de lanzamientos: {e}")

async def import_existing_links():
    from sent_articles import save_article
    bot = Bot(token=BOT_TOKEN)
    try:
        updates = await bot.get_updates(limit=100)
        for update in updates:
            if update.message and update.message.text:
                links = [word for word in update.message.text.split() if word.startswith('http')]
                for link in links:
                    save_article(link)
        print("✅ Importación completada.")
    except Exception as e:
        print(f"Error importando mensajes antiguos: {e}")


async def start_bot():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    job_queue = application.job_queue
    await import_existing_links()
    job_queue.run_repeating(check_feeds, interval=600, first=10)

    print("Bot iniciado correctamente.")
    await application.run_polling()

def main():
    asyncio.run(start_bot())




if __name__ == "__main__":
    main()
