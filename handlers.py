# handlers.py
from telegram import Update, BotCommand
from telegram.ext import ContextTypes, filters
from ai_client import ai_client
from database import (
    save_message,
    save_user,
    user_exists,
    save_group,
    get_conversation_context,
    get_last_reply,
    get_config,
    update_config,
    get_group_info
)
import logging
from config import (
    BOT_NAME,
    BOT_USERNAME,
    MAX_HISTORY_MESSAGES,
    RESPONSE_STRATEGIES,
    DEFAULT_CONFIG
)
import re
from typing import Optional

logger = logging.getLogger(__name__)

async def setup_commands(bot):
    """Configura os comandos do bot"""
    commands = [
        BotCommand("start", "Inicia o bot"),
        BotCommand("help", "Mostra ajuda"),
        BotCommand("info", "Informações do bot"),
        BotCommand("resumo", "Mostra histórico da conversa"),
        BotCommand("config", "Configurações do bot"),
        BotCommand("model", "Altera modelo de IA"),
        BotCommand("status", "Status do bot")
    ]
    await bot.set_my_commands(commands)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipula o comando /start"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        await save_user(user.id, user.full_name)
        if chat.type != "private":
            await save_group(chat.id, chat.title, user.id)
        
        response = (
            f"👋 Olá {user.first_name}! Eu sou {BOT_NAME}, seu assistente de IA.\n\n"
            "Posso ajudar com:\n"
            "- Respostas inteligentes às suas perguntas\n"
            "- Manter o contexto das conversas\n"
            "- Corrigir informações incorretas\n\n"
            f"Me marque com @{BOT_USERNAME} ou use /help para comandos."
        )
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Erro em /start: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Ocorreu um erro ao processar seu comando.")

async def handle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipula o comando /info"""
    try:
        model_info = await ai_client.list_models()
        models_list = "\n".join([f"- {name}" for name in model_info.keys()])
        
        response = (
            f"🤖 *{BOT_NAME} - Informações*\n\n"
            "🔧 *Funcionalidades:*\n"
            "- Respostas contextuais inteligentes\n"
            "- Correção de informações\n"
            "- Suporte a múltiplos modelos de IA\n"
            "- Configuração flexível\n\n"
            "📊 *Modelos disponíveis:*\n"
            f"{models_list}\n\n"
            "Use /config para personalizar."
        )
        
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Erro em /info: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Não consegui obter informações no momento.")

async def handle_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipula o comando /config"""
    try:
        chat = update.effective_chat
        user = update.effective_user
        
        # Verificar se é admin
        if not await is_admin(chat.id, user.id):
            await update.message.reply_text("🚫 Acesso restrito a administradores.")
            return
        
        args = context.args
        config = await get_config()
        
        if not args:
            current_settings = "\n".join([f"- {k}: {v}" for k, v in config.items()])
            strategies = "\n".join([f"- {k}: {v}" for k, v in RESPONSE_STRATEGIES.items()])
            
            response = (
                f"⚙️ *Configurações Atuais*\n\n"
                f"{current_settings}\n\n"
                "*Estratégias disponíveis:*\n"
                f"{strategies}\n\n"
                "Use /config <chave> <valor> para alterar."
            )
            
            await update.message.reply_text(response, parse_mode="Markdown")
            return
        
        if len(args) < 2:
            await update.message.reply_text("Formato: /config <chave> <valor>")
            return
        
        key, value = args[0], args[1]
        
        if key not in DEFAULT_CONFIG:
            await update.message.reply_text(f"Chave inválida. Opções: {', '.join(DEFAULT_CONFIG.keys())}")
            return
        
        config[key] = value
        await update_config(config)
        
        await update.message.reply_text(f"✅ Configuração atualizada:\n\n*{key}* = `{value}`", parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Erro em /config: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Erro ao atualizar configuração.")

async def is_admin(chat_id: int, user_id: int) -> bool:
    """Verifica se o usuário é admin do grupo"""
    try:
        chat_info = await get_group_info(chat_id)
        if not chat_info:
            return False
            
        return user_id == chat_info['creator_id'] or user_id in chat_info.get('admins', [])
    except Exception as e:
        logger.error(f"Erro ao verificar admin: {str(e)}")
        return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipula mensagens regulares"""
    try:
        message = update.message
        if not message or not message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        text = message.text.strip()
        
        if len(text) < 3 or text.startswith('/'):
            return
        
        await save_user(user.id, user.full_name)
        if chat.type != "private":
            await save_group(chat.id, chat.title, user.id)
        
        await save_message(chat.id, user.id, user.full_name, text, is_bot=False)
        
        should_reply = await should_respond(message, context)
        
        if should_reply:
            context_messages = await get_conversation_context(chat.id, MAX_HISTORY_MESSAGES)
            response = await ai_client.generate_response(context_messages, chat.id)
            
            if response:
                await message.reply_text(response)
                await save_message(chat.id, context.bot.id, BOT_NAME, response, is_bot=True)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
        await update.message.reply_text("⚠️ Ocorreu um erro ao processar sua mensagem.")

async def should_respond(message, context) -> bool:
    """Determina se o bot deve responder à mensagem"""
    try:
        text = message.text.lower()
        chat = message.chat
        
        if BOT_USERNAME.lower() in text:
            return True
        
        config = await get_config()
        strategy = config.get('response_strategy', 'smart')
        
        if strategy == "mention":
            return False
        elif strategy == "active":
            return True
        
        if '?' in text:
            return True
            
        if any(keyword in text for keyword in ['sabe', 'como funciona', 'explique', 'ajuda']):
            return True
            
        last_reply = await get_last_reply(chat.id)
        if last_reply and not last_reply.get('accurate', True):
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Erro em should_respond: {str(e)}")
        return False

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipula novos membros no grupo"""
    try:
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                await update.message.reply_text(
                    f"👋 Olá a todos! Eu sou {BOT_NAME}, seu assistente de IA. "
                    "Estou aqui para ajudar com perguntas e conversas!"
                )
            else:
                if not await user_exists(member.id):
                    await update.message.reply_text(
                        f"🌟 Bem-vindo(a), {member.full_name}!\n"
                        f"Se precisar de algo, é só me marcar com @{BOT_USERNAME}!"
                    )
                await save_user(member.id, member.full_name)
                
    except Exception as e:
        logger.error(f"Erro em handle_new_members: {str(e)}", exc_info=True)
