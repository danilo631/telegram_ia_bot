# ai_client.py
import requests
from config import OPENROUTER_API_KEY, IA_MODEL

def gerar_resposta(contexto: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": IA_MODEL,
        "messages": [
            {"role": "system", "content": "Você é um assistente que responde com base nas mensagens do grupo."},
            {"role": "user", "content": contexto}
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[ERRO IA]: {e}"
