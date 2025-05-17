# ai_client.py
import aiohttp
import asyncio
from config import (
    OPENROUTER_API_KEY,
    IA_MODEL,
    BOT_NAME,
    BOT_TRIGGERS,
    CORRECTION_PROMPT,
    DEFAULT_PROMPT
)
import logging
from typing import Optional, Tuple
import re

logger = logging.getLogger(__name__)

# Inicialização da IA
def initialize_ai():
    logger.info(f"Configurando IA com modelo: {IA_MODEL}")

async def gerar_resposta(contexto: str, chat_id: int, is_mention: bool = False) -> Optional[str]:
    """Gera uma resposta usando IA com base no contexto"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": f"https://telegram-group-{chat_id}",
    }
    
    system_prompt = DEFAULT_PROMPT.format(bot_name=BOT_NAME)
    if is_mention:
        system_prompt += (
            "\n\nO usuário te mencionou diretamente. "
            "Responda de forma completa e direta à solicitação."
        )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": contexto}
    ]
    
    payload = {
        "model": IA_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                
                if not data.get("choices"):
                    logger.error(f"Resposta inesperada da API: {data}")
                    return None
                
                resposta = data["choices"][0]["message"]["content"].strip()
                return clean_response(resposta)
                
    except asyncio.TimeoutError:
        logger.warning("Timeout ao acessar a API do OpenRouter")
        return None
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
        return None

async def should_respond(message, context, last_reply: dict = None) -> bool:
    """Determina se o bot deve responder a uma mensagem"""
    texto = message.text.lower()
    
    # Responde sempre a menções
    if context.bot.username.lower() in texto.lower():
        return True
    
    # Verifica triggers de palavras-chave
    if any(trigger.lower() in texto for trigger in BOT_TRIGGERS):
        return True
    
    # Verifica se é uma pergunta
    if '?' in texto and len(texto.split()) > 3:
        return True
    
    # Verifica se a última resposta foi incorreta
    if last_reply and not last_reply.get('accurate', True):
        return True
    
    # Outras estratégias de resposta
    return False

def clean_response(text: str) -> str:
    """Limpa a resposta da IA"""
    if not text:
        return ""
    
    # Remove citações indesejadas
    text = re.sub(r'^["\']|["\']$', '', text)
    
    # Remove múltiplos espaços e quebras de linha
    text = ' '.join(text.split())
    
    # Garante que termina com pontuação
    if text and text[-1] not in {'.', '!', '?'}:
        text += '.'
    
    return text[:500]  # Limite de caracteres
