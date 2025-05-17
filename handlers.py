# handlers.py
from telegram import Update
from telegram.ext import CallbackContext
from ai_client import gerar_resposta
from database import salvar_mensagem, obter_ultimas_mensagens

def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update.effective_user.full_name or "Usuário"
    texto = update.message.text

    salvar_mensagem(chat_id, user, texto)

    contexto_mensagens = obter_ultimas_mensagens(chat_id, limite=1000)
    prompt = "\n".join(contexto_mensagens)
    resposta = gerar_resposta(prompt)

    update.message.reply_text(resposta)

def handle_comandos(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    comando = update.message.text.lower()

    if comando == "/resumo":
        ultimas = obter_ultimas_mensagens(chat_id, limite=50)
        update.message.reply_text("📝 Últimas mensagens:\n\n" + "\n".join(ultimas))
    elif comando == "/info":
        update.message.reply_text("🤖 Eu sou um bot com IA que responde com base nas mensagens anteriores do grupo.")
