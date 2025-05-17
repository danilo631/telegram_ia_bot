# main.py
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from handlers import handle_message, handle_comandos
from config import TELEGRAM_TOKEN
from threading import Thread
from painel import iniciar_painel

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler(["resumo", "info"], handle_comandos))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🤖 Bot iniciado...")

    Thread(target=iniciar_painel).start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
