# handlers.py
from telegram import Update
from telegram.ext import CallbackContext
from ai_client import gerar_resposta
from database import (
    salvar_mensagem, 
    obter_contexto_conversa,
    salvar_usuario
)
import re

async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name or "Usuário"
    texto = update.message.text
    
    # Salva informações do usuário
    salvar_usuario(user_id, user_name)
    
    # Remove comandos e mensagens muito curtas do contexto
    if texto.startswith('/') or len(texto.strip()) < 3:
        return
    
    # Salva mensagem no histórico
    salvar_mensagem(chat_id, user_id, user_name, texto, is_bot=False)
    
    # Obtém contexto relevante da conversa
    contexto = obter_contexto_conversa(chat_id)
    
    # Gera resposta usando IA
    resposta = await gerar_resposta(contexto, chat_id)
    
    # Envia resposta e salva no histórico
    if resposta and len(resposta.strip()) > 0:
        await update.message.reply_text(resposta)
        salvar_mensagem(chat_id, context.bot.id, "Bot", resposta, is_bot=True)

async def handle_comandos(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    comando = update.message.text.lower()
    
    if comando.startswith('/resumo'):
        contexto = obter_contexto_conversa(chat_id, limite=10)
        await update.message.reply_text(f"📝 Resumo da conversa:\n\n{contexto}")
    elif comando.startswith('/info'):
        await update.message.reply_text(
            "🤖 Eu sou um bot inteligente que ajuda no grupo!\n"
            "Posso responder perguntas, manter conversas e ajudar com informações.\n"
            "Use /resumo para ver um resumo da conversa recente."
        )

async def handle_new_members(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(
                "Olá a todos! 🤖 Sou o assistente de IA deste grupo. "
                "Estou aqui para ajudar com perguntas e conversas. "
                "É um prazer estar aqui!"
            )
        else:
            await update.message.reply_text(
                f"Seja bem-vindo(a), {member.full_name}! 👋\n"
                "Se precisar de algo, é só chamar!"
            )
