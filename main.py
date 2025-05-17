# main.py
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram.ext import filters
from telegram import Update
from threading import Thread
import asyncio

from handlers import handle_message, handle_comandos, handle_new_members
from config import TELEGRAM_TOKEN, DATA_DIR, MESSAGES_FILE, USERS_FILE
from painel import iniciar_painel
from database import initialize_database

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot iniciado com sucesso! Digite /info para ver minhas funcionalidades.")

def main():
    # Inicializa o banco de dados
    initialize_database()
    
    # Configuração de logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(DATA_DIR / 'bot.log'),
            logging.StreamHandler()
        ]
    )

    # Criação da aplicação
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["resumo", "info"], handle_comandos))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))

    # Inicia o painel em thread separada
    Thread(target=iniciar_painel, daemon=True).start()

    logging.info("🤖 Bot iniciado com sucesso!")
    print("🤖 Bot iniciado com sucesso!")

    # Inicia o bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}", exc_info=True)
        print(f"Erro fatal: {str(e)}")
