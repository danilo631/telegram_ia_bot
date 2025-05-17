# config.py
from pathlib import Path
import os

# Configurações básicas
BOT_NAME = "SuperAI"
BOT_USERNAME = "SuperAi148_bot"  # Substitua pelo seu username real

# Tokens e configurações da API
TELEGRAM_TOKEN = '7586808863:AAEM92xbhc8TP8VSGz8QdTBaJOu3jwhuiNA'
OPENROUTER_API_KEY = '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'
IA_MODEL = 'meta-llama/llama-4-maverick:free'  # Modelo padrão

# Configurações de arquivos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Arquivos JSON
MESSAGES_FILE = DATA_DIR / 'messages.json'
USERS_FILE = DATA_DIR / 'users.json'
CONFIG_FILE = DATA_DIR / 'config.json'
GROUPS_FILE = DATA_DIR / 'groups.json'

# Limites
MAX_CONTEXT_LENGTH = 3000  # Aumentado para contexto mais longo
MAX_HISTORY_MESSAGES = 20
MAX_MESSAGES_STORED = 2000

# Estratégias de resposta
RESPONSE_STRATEGIES = {
    "smart": "Responde quando relevante",
    "active": "Responde sempre que possível",
    "mention": "Responde apenas quando mencionado"
}

# Configuração padrão
DEFAULT_CONFIG = {
    "response_strategy": "smart",
    "language": "pt-br",
    "max_tokens": 500,
    "temperature": 0.7
}

# Prompt do sistema
SYSTEM_PROMPT = f"""Você é {BOT_NAME}, um assistente de IA avançado em grupos do Telegram. Siga estas diretrizes:

1. Quando mencionado (@), responda imediatamente de forma completa
2. Para perguntas diretas, seja conciso (1-3 frases)
3. Corrija informações incorretas de forma educada
4. Mantenha o contexto da conversa
5. Use tom natural e emojis quando apropriado 🤖
6. Se não souber algo, seja honesto
7. Para perguntas complexas, peça mais detalhes
8. Interaja naturalmente com os membros do grupo

Contexto atual da conversa:"""

# Modelos disponíveis na OpenRouter
AVAILABLE_MODELS = {
    "llama3": "meta-llama/llama-3-70b-instruct:nitro",
    "maverick": "meta-llama/llama-4-maverick:free",
    "claude": "anthropic/claude-3-haiku"
}
