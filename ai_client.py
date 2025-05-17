# ai_client.py
import aiohttp
import asyncio
from config import OPENROUTER_API_KEY, IA_MODEL
import json
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

async def gerar_resposta(contexto: str, chat_id: int) -> Optional[str]:
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": f"https://telegram-bot-{chat_id}",
    }
    
    messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente inteligente em um grupo do Telegram. "
                "Sua função é participar de conversas de forma natural e útil, "
                "respondendo perguntas e interagindo com os membros do grupo. "
                "Seja conciso e direto nas respostas. "
                "Adapte-se ao tom da conversa e só intervenha quando for relevante. "
                "Cumprimente novos membros e responda perguntas de forma clara. "
                "Se não souber algo, seja honesto. "
                "Mantenha o contexto da conversa mas não repita informações."
            )
        },
        {"role": "user", "content": contexto}
    ]
    
    payload = {
        "model": IA_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                
                if "choices" not in data or len(data["choices"]) == 0:
                    logger.error("Resposta da API sem choices: %s", json.dumps(data, indent=2))
                    return None
                
                resposta = data["choices"][0]["message"]["content"].strip()
                
                # Limpeza da resposta
                resposta = resposta.replace('"', '')
                resposta = resposta.split('\n')[0] if '\n' in resposta else resposta
                
                return resposta if len(resposta) > 0 else None
                
    except asyncio.TimeoutError:
        logger.error("Timeout ao acessar a API do OpenRouter")
        return "⏳ Estou processando sua mensagem, por favor aguarde..."
    except Exception as e:
        logger.error("Erro ao gerar resposta: %s", str(e), exc_info=True)
        return None
