# main.py
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from handlers import handle_message, handle_comandos, handle_new_members
from config import TELEGRAM_TOKEN
from threading import Thread
from painel import iniciar_painel
import logging

def main():
    # Configuração básica de logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler(["resumo", "info"], handle_comandos))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, handle_new_members))

    print("🤖 Bot iniciado com sucesso!")
    
    # Inicia o painel em uma thread separada
    Thread(target=iniciar_painel, daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
