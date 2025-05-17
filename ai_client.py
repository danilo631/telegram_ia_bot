# ai_client.py
import aiohttp
import asyncio
from config import (
    OPENROUTER_API_KEY,
    IA_MODEL,
    BOT_NAME,
    DEFAULT_PROMPT,
    CORRECTION_PROMPT
)
import logging
from typing import Optional
import re

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

    async def gerar_resposta(self, contexto: str, chat_id: int, is_mention: bool = False) -> Optional[str]:
        try:
            messages = [{
                "role": "system",
                "content": DEFAULT_PROMPT + ("\n\nUsuário te mencionou diretamente! Responda de forma completa." if is_mention else "")
            }, {
                "role": "user", 
                "content": contexto
            }]

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
                return self.clean_response(data['choices'][0]['message']['content'])

        except Exception as e:
            logger.error(f"Erro na IA: {e}", exc_info=True)
            return None

    def clean_response(self, text: str) -> str:
        text = re.sub(r'^\W+|\W+$', '', text)
        return text[:500]

    async def close(self):
        await self.session.close()

# Instância global
ai_client = AIClient()

async def gerar_resposta(*args, **kwargs):
    return await ai_client.gerar_resposta(*args, **kwargs)
