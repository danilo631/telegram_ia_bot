# ai_client.py
import aiohttp
import asyncio
from config import OPENROUTER_API_KEY, IA_MODEL
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def gerar_resposta(contexto: str, chat_id: int) -> Optional[str]:
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": f"https://telegram-group-{chat_id}",
    }
    
    messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente inteligente em um grupo do Telegram. "
                "Siga estas diretrizes:\n"
                "1. Seja natural e conversacional\n"
                "2. Responda de forma concisa (1-2 frases)\n"
                "3. Só responda quando for relevante\n"
                "4. Cumprimente novos membros\n"
                "5. Se não souber algo, diga\n"
                "6. Mantenha o contexto mas não repita informações\n"
                "7. Adapte-se ao tom da conversa\n"
                "8. Use emojis quando apropriado\n\n"
                "Contexto atual:\n{contexto}"
            )
        },
        {"role": "user", "content": contexto}
    ]
    
    payload = {
        "model": IA_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150,
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
                
                # Limpeza básica da resposta
                resposta = resposta.replace('"', '').replace("'", "")
                
                # Remove múltiplas quebras de linha
                resposta = ' '.join(resposta.splitlines())
                
                return resposta if len(resposta) > 1 else None
                
    except asyncio.TimeoutError:
        logger.warning("Timeout ao acessar a API do OpenRouter")
        return None
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
        return None
