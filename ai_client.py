# ai_client.py
import aiohttp
import asyncio
from config import (
    OPENROUTER_API_KEY,
    IA_MODEL,
    BOT_NAME,
    BOT_USERNAME,
    DEFAULT_PROMPT,
    CORRECTION_PROMPT
)
import logging
from typing import Optional, Tuple
import re

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": f"https://{BOT_USERNAME}-bot"
        }

    async def gerar_resposta(self, contexto: str, chat_id: int, is_mention: bool = False) -> Optional[str]:
        """Gera uma resposta usando IA com base no contexto"""
        try:
            system_prompt = DEFAULT_PROMPT
            if is_mention:
                system_prompt += "\n\nO usuário te mencionou diretamente. Responda de forma completa e precisa."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": contexto}
            ]

            payload = {
                "model": IA_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 300
            }

            async with self.session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                if not data.get("choices"):
                    logger.error(f"Resposta inesperada da API: {data}")
                    return None
                
                resposta = data["choices"][0]["message"]["content"].strip()
                return self.clean_response(resposta)

        except asyncio.TimeoutError:
            logger.warning("Timeout ao acessar a API do OpenRouter")
            return None
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
            return None

    async def should_respond(self, message_text: str, last_reply: dict = None) -> bool:
        """Determina se o bot deve responder a uma mensagem"""
        texto = message_text.lower()
        
        # Responde sempre a menções
        if BOT_USERNAME.lower() in texto:
            return True
        
        # Verifica se é uma pergunta
        if '?' in texto and len(texto.split()) > 3:
            return True
        
        # Verifica se a última resposta foi incorreta
        if last_reply and not last_reply.get('accurate', True):
            return True
        
        # Outras estratégias de resposta
        return False

    def clean_response(self, text: str) -> str:
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

    async def close(self):
        await self.session.close()

# Instância global
ai_client = AIClient()

# Funções de interface
async def gerar_resposta(*args, **kwargs):
    return await ai_client.gerar_resposta(*args, **kwargs)

async def should_respond(*args, **kwargs):
    return await ai_client.should_respond(*args, **kwargs)
