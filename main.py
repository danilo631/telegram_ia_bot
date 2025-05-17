# main.py
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
from handlers import (
    handle_commands,
    handle_message,
    handle_mention,
    handle_config
)
from config import TELEGRAM_TOKEN, BOT_NAME
from database import db
from ai_client import ai_client
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(app):
    await db.initialize()
    await app.bot.set_my_commands([
        ("start", "Inicia o bot"),
        ("help", "Ajuda"),
        ("info", "Informações"),
        ("resumo", "Histórico"),
        ("config", "Configurações")
    ])

async def shutdown(app):
    await ai_client.close()
    logger.info("Bot encerrado")

def main():
    app = ApplicationBuilder() \
        .token(TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .post_shutdown(shutdown) \
        .build()

    # Handlers
    app.add_handler(CommandHandler(["start", "help", "info", "resumo"], handle_commands))
    app.add_handler(CommandHandler("config", handle_config))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Entity("mention"), handle_mention))

    logger.info(f"🤖 {BOT_NAME} iniciando...")
    app.run_polling()

if __name__ == "__main__":
    main()
