# handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from ai_client import gerar_resposta
from database import (
    salvar_mensagem, 
    obter_contexto_conversa,
    salvar_usuario,
    usuario_existe
)
import logging
from config import MAX_HISTORY_MESSAGES

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        user_name = update.effective_user.full_name or "Usuário"
        texto = update.message.text.strip()

        # Ignora mensagens muito curtas ou comandos
        if len(texto) < 2 or texto.startswith('/'):
            return

        # Salva/atualiza informações do usuário
        await salvar_usuario(user_id, user_name)
        
        # Salva mensagem no histórico
        await salvar_mensagem(chat_id, user_id, user_name, texto, is_bot=False)
        
        # Obtém contexto relevante da conversa
        contexto = await obter_contexto_conversa(chat_id, limite=MAX_HISTORY_MESSAGES)
        
        # Gera resposta usando IA
        resposta = await gerar_resposta(contexto, chat_id)
        
        # Envia resposta se for válida
        if resposta and len(resposta.strip()) > 1:
            await update.message.reply_text(resposta)
            await salvar_mensagem(chat_id, context.bot.id, context.bot.first_name, resposta, is_bot=True)

    except Exception as e:
        logger.error(f"Erro em handle_message: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Ocorreu um erro ao processar sua mensagem.")

async def handle_comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        comando = update.message.text.lower().split()[0]

        if comando == "/resumo":
            contexto = await obter_contexto_conversa(chat_id, limite=10)
            await update.message.reply_text(f"📝 Últimas mensagens:\n\n{contexto}")
        elif comando == "/info":
            await update.message.reply_text(
                "🤖 *Informações do Bot*\n\n"
                "Eu sou um assistente inteligente para grupos do Telegram!\n"
                "Posso:\n"
                "- Responder perguntas\n"
                "- Manter conversas contextualizadas\n"
                "- Ajudar com informações\n\n"
                "Comandos disponíveis:\n"
                "/info - Mostra esta mensagem\n"
                "/resumo - Mostra um resumo da conversa recente",
                parse_mode="Markdown"
            )

    except Exception as e:
        logger.error(f"Erro em handle_comandos: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Ocorreu um erro ao processar o comando.")

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                await update.message.reply_text(
                    "👋 Olá a todos! Sou o assistente inteligente deste grupo. "
                    "Estou aqui para ajudar com perguntas e manter conversas interessantes!"
                )
            else:
                # Verifica se é um novo usuário
                if not await usuario_existe(member.id):
                    await update.message.reply_text(
                        f"🌟 Bem-vindo(a) ao grupo, {member.full_name}!\n"
                        "Se precisar de algo, é só chamar!"
                    )
                await salvar_usuario(member.id, member.full_name)
                
    except Exception as e:
        logger.error(f"Erro em handle_new_members: {str(e)}", exc_info=True)
