# main.py
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram import Update
from handlers import (
    handle_start,
    handle_info,
    handle_config,
    handle_message,
    setup_commands
)
from config import TELEGRAM_TOKEN, BOT_NAME, DATA_DIR
from database import db
from ai_client import ai_client
import asyncio

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
    """Executado após a inicialização"""
    await db.initialize()
    await setup_commands(application.bot)
    logger.info(f"{BOT_NAME} inicializado com sucesso")

async def shutdown(application):
    """Executado no encerramento"""
    await ai_client.close()
    logger.info("Conexões encerradas corretamente")

def main():
    """Função principal"""
    try:
        # Criar aplicação
        app = ApplicationBuilder() \
            .token(TELEGRAM_TOKEN) \
            .post_init(post_init) \
            .post_shutdown(shutdown) \
            .build()

        # Handlers de comandos
        app.add_handler(CommandHandler("start", handle_start))
        app.add_handler(CommandHandler("info", handle_info))
        app.add_handler(CommandHandler("config", handle_config))
        
        # Handler de mensagens
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info(f"Iniciando {BOT_NAME}...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.critical(f"Falha ao iniciar bot: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
