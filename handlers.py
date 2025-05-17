# handlers.py
from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from ai_client import gerar_resposta, should_respond
from database import (
    salvar_mensagem,
    obter_contexto_conversa,
    salvar_usuario,
    usuario_existe,
    get_last_reply,
    get_config,
    update_config
)
import logging
from config import (
    BOT_NAME,
    MAX_HISTORY_MESSAGES,
    DEFAULT_CONFIG,
    RESPONSE_STRATEGIES
)
import re

logger = logging.getLogger(__name__)

async def setup_commands(bot):
    commands = [
        BotCommand("start", "Inicia o bot"),
        BotCommand("help", "Ajuda"),
        BotCommand("info", "Informações"),
        BotCommand("resumo", "Mostra histórico"),
        BotCommand("config", "Configurações")
    ]
    await bot.set_my_commands(commands)

async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        command = update.message.text.split()[0].lower()
        chat_id = update.effective_chat.id
        
        if command == "/start":
            response = f"""👋 Olá! Eu sou {BOT_NAME}, seu assistente de IA!
            
Comandos disponíveis:
/info - Minhas informações
/resumo - Histórico da conversa
/config - Configurações

Me marque com @ para respostas imediatas!"""
        
        elif command == "/info":
            response = f"""🤖 *{BOT_NAME} - Informações*

- Responde a menções @{BOT_USERNAME}
- Corrige informações erradas
- Mantém contexto de conversas
- Aprende com interações

Versão 2.0 | IA: {IA_MODEL}"""
        
        elif command == "/resumo":
            contexto = await obter_contexto_conversa(chat_id, 5)
            response = f"📝 *Últimas mensagens:*\n\n{contexto}"
        
        elif command == "/config":
            config = await get_config()
            strategies = "\n".join([f"- {k}: {v}" for k,v in RESPONSE_STRATEGIES.items()])
            response = f"""⚙️ *Configurações Atuais*

Estratégia: {config['response_strategy']}
Idioma: {config['language']}

*Opções disponíveis:*
{strategies}

Use /config <chave> <valor> para alterar"""
        
        else:
            response = "Comando desconhecido. Use /help para ajuda."

        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Erro em comandos: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Erro ao processar comando.")

async def handle_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_admin(update.effective_user.id):
            await update.message.reply_text("🚫 Acesso restrito a administradores")
            return

        args = update.message.text.split()[1:]
        if len(args) < 2:
            await update.message.reply_text("Formato: /config <chave> <valor>")
            return

        key, value = args[0], args[1]
        config = await get_config()
        
        if key not in DEFAULT_CONFIG:
            await update.message.reply_text(f"Chave inválida. Opções: {', '.join(DEFAULT_CONFIG.keys())}")
            return

        config[key] = value
        await update_config(config)
        await update.message.reply_text(f"✅ Configuração atualizada: {key} = {value}")

    except Exception as e:
        logger.error(f"Erro em config: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Erro ao atualizar configuração.")

async def is_admin(user_id: int) -> bool:
    config = await get_config()
    return user_id in config['admin_ids']
