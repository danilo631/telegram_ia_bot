import logging
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram.ext import filters
from telegram import Update
from threading import Thread

from handlers import handle_message, handle_comandos, handle_new_members
from config import TELEGRAM_TOKEN
from painel import iniciar_painel


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot iniciado com sucesso!")


def main():
    # Configuração de logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Criação da aplicação
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler(["resumo", "info"], handle_comandos))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))

    # Inicia o painel em thread separada
    Thread(target=iniciar_painel, daemon=True).start()

    print("🤖 Bot iniciado com sucesso!")

    # Inicia o bot
    app.run_polling()


if __name__ == "__main__":
    main()
