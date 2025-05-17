# ai_client.py
import aiohttp
import asyncio
from config import (
    OPENROUTER_API_KEY,
    IA_MODEL,
    BOT_NAME,
    SYSTEM_PROMPT,
    DEFAULT_CONFIG,
    AVAILABLE_MODELS
)
import logging
from typing import Optional, Dict
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/telegram-bot",
        }
        self.model = IA_MODEL
        self.last_request = None

    async def generate_response(self, prompt: str, chat_id: int, is_mention: bool = False) -> Optional[str]:
        """Gera uma resposta usando a API da OpenRouter"""
        try:
            current_time = datetime.now()
            if self.last_request and (current_time - self.last_request).seconds < 1:
                await asyncio.sleep(1)  # Rate limiting
            
            self.last_request = current_time

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": DEFAULT_CONFIG["temperature"],
                "max_tokens": DEFAULT_CONFIG["max_tokens"],
                "metadata": {
                    "chat_id": chat_id,
                    "is_mention": is_mention
                }
            }

            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                if not data.get('choices'):
                    logger.error(f"Resposta inesperada: {json.dumps(data, indent=2)}")
                    return None
                
                return data['choices'][0]['message']['content'].strip()

        except asyncio.TimeoutError:
            logger.warning("Timeout na requisição à OpenRouter API")
            return "⏳ Estou processando sua solicitação, por favor aguarde..."
        except aiohttp.ClientError as e:
            logger.error(f"Erro na conexão: {str(e)}")
            return "🔌 Estou tendo problemas para me conectar ao servidor."
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
            return None

    async def list_models(self) -> Dict:
        """Lista modelos disponíveis na OpenRouter"""
        try:
            async with self.session.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=15
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {str(e)}")
            return AVAILABLE_MODELS

    async def change_model(self, model_key: str) -> bool:
        """Altera o modelo de IA sendo usado"""
        if model_key in AVAILABLE_MODELS:
            self.model = AVAILABLE_MODELS[model_key]
            return True
        return False

    async def close(self):
        await self.session.close()

# Instância global
ai_client = AIClient()
