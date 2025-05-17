# main.py
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram.ext import filters
from telegram import Update
from threading import Thread
import asyncio

from handlers import (
    handle_message,
    handle_commands,
    handle_config,
    handle_new_members,
    handle_mention,
    setup_commands
)
from config import TELEGRAM_TOKEN, BOT_NAME, DATA_DIR
from painel import iniciar_painel
from database import initialize_database
from ai_client import ai_client

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(DATA_DIR / 'bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Configurações pós-inicialização"""
    await initialize_database()
    await setup_commands(application.bot)
    logger.info("Comandos do bot configurados")

async def shutdown(application):
    """Encerramento limpo"""
    await ai_client.close()
    logger.info("Conexões encerradas corretamente")

def main():
    # Criação da aplicação
    app = ApplicationBuilder() \
        .token(TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .post_shutdown(shutdown) \
        .build()

    # Handlers
    app.add_handler(CommandHandler(["start", "info", "resumo"], handle_commands))
    app.add_handler(CommandHandler("config", handle_config))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))
    app.add_handler(MessageHandler(filters.TEXT & filters.Entity("mention"), handle_mention))

    # Inicia o painel em thread separada
    Thread(target=iniciar_painel, daemon=True).start()

    logger.info(f"🤖 {BOT_NAME} iniciado com sucesso!")
    print(f"🤖 {BOT_NAME} iniciado com sucesso!")

    # Inicia o bot
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Erro fatal: {str(e)}", exc_info=True)
        print(f"Erro fatal: {str(e)}")
