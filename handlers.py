# handlers.py
from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from ai_client import gerar_resposta, should_respond
from database import (
    salvar_mensagem,
    obter_contexto_conversa,
    salvar_usuario,
    usuario_existe,
    get_last_reply
)
import logging
from config import (
    BOT_NAME,
    MAX_HISTORY_MESSAGES,
    BOT_TRIGGERS,
    RESPONSE_STRATEGY
)
import re

logger = logging.getLogger(__name__)

async def setup_commands(bot):
    """Configura os comandos do bot"""
    commands = [
        BotCommand("start", "Inicia o bot"),
        BotCommand("info", "Informações sobre o bot"),
        BotCommand("resumo", "Mostra resumo da conversa"),
        BotCommand("config", "Configurações do bot")
    ]
    await bot.set_my_commands(commands)

async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        command = update.message.text.split()[0].lower()
        
        if command == "/start":
            response = (
                f"👋 Olá! Eu sou o {BOT_NAME}, seu assistente de IA no Telegram!\n\n"
                "Você pode me mencionar com @ ou usar um destes comandos:\n"
                "/info - Mostra minhas informações\n"
                "/resumo - Mostra o contexto atual\n"
                "/config - Configurações (para admins)"
            )
        elif command == "/info":
            response = (
                f"🤖 *{BOT_NAME} - Informações*\n\n"
                "Eu sou um assistente inteligente com:\n"
                "- Respostas contextuais\n"
                "- Correção de informações\n"
                "- Respostas a menções\n"
                "- Aprendizado contínuo\n\n"
                f"Me acione com @{context.bot.username} ou quando precisar de ajuda!"
            )
        elif command == "/resumo":
            contexto = await obter_contexto_conversa(update.effective_chat.id, 10)
            response = f"📝 *Últimas mensagens:*\n\n{contexto}"
        elif command == "/config":
            response = "⚙️ *Configurações* (acesso restrito)"
        
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Erro em handle_commands: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Ocorreu um erro ao processar o comando.")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return

        # Verifica se a menção é para este bot
        if context.bot.username.lower() not in update.message.text.lower():
            return

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        user_name = update.effective_user.full_name or "Usuário"
        texto = re.sub(r'@\w+\s*', '', update.message.text).strip()

        if len(texto) < 2:
            return

        await salvar_usuario(user_id, user_name)
        await salvar_mensagem(chat_id, user_id, user_name, texto, is_bot=False)

        contexto = await obter_contexto_conversa(chat_id, MAX_HISTORY_MESSAGES)
        resposta = await gerar_resposta(contexto, chat_id, is_mention=True)

        if resposta and len(resposta.strip()) > 1:
            await update.message.reply_text(resposta)
            await salvar_mensagem(chat_id, context.bot.id, BOT_NAME, resposta, is_bot=True)

    except Exception as e:
        logger.error(f"Erro em handle_mention: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Ocorreu um erro ao processar sua menção.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        user_name = update.effective_user.full_name or "Usuário"
        texto = update.message.text.strip()

        # Ignora mensagens muito curtas ou comandos
        if len(texto) < 3 or texto.startswith('/'):
            return

        await salvar_usuario(user_id, user_name)
        await salvar_mensagem(chat_id, user_id, user_name, texto, is_bot=False)

        # Verifica se deve responder
        should_reply = await should_respond(
            update.message, 
            context,
            last_reply=await get_last_reply(chat_id)
        )

        if should_reply:
            contexto = await obter_contexto_conversa(chat_id, MAX_HISTORY_MESSAGES)
            resposta = await gerar_resposta(contexto, chat_id, is_mention=False)

            if resposta and len(resposta.strip()) > 1:
                await update.message.reply_text(resposta)
                await salvar_mensagem(chat_id, context.bot.id, BOT_NAME, resposta, is_bot=True)

    except Exception as e:
        logger.error(f"Erro em handle_message: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Ocorreu um erro ao processar sua mensagem.")

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                await update.message.reply_text(
                    f"👋 Olá a todos! Eu sou o {BOT_NAME}, seu assistente de IA. "
                    "Estou aqui para ajudar com perguntas e manter conversas interessantes!"
                )
            else:
                if not await usuario_existe(member.id):
                    await update.message.reply_text(
                        f"🌟 Bem-vindo(a), {member.full_name}!\n"
                        f"Se precisar de algo, é só me marcar com @{context.bot.username}!"
                    )
                await salvar_usuario(member.id, member.full_name)
                
    except Exception as e:
        logger.error(f"Erro em handle_new_members: {str(e)}", exc_info=True)
