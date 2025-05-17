# config.py
from pathlib import Path

# Configurações básicas
BOT_NAME = "SuperAI"
BOT_USERNAME = "SuperAi148_bot"

# Tokens atualizados
TELEGRAM_TOKEN = '7586808863:AAEM92xbhc8TP8VSGz8QdTBaJOu3jwhuiNA'
OPENROUTER_API_KEY = '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'
IA_MODEL = 'meta-llama/llama-4-maverick:free'

# Configurações de arquivos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Arquivos JSON
MESSAGES_FILE = DATA_DIR / 'messages.json'
USERS_FILE = DATA_DIR / 'users.json'
CONFIG_FILE = DATA_DIR / 'config.json'

# Limites
MAX_CONTEXT_LENGTH = 2000
MAX_HISTORY_MESSAGES = 15
MAX_MESSAGES_STORED = 1000

# Estratégias
RESPONSE_STRATEGIES = {
    "smart": "Responde apenas quando relevante",
    "always": "Responde a todas as mensagens",
    "mention": "Responde apenas quando mencionado"
}

# Configuração padrão
DEFAULT_CONFIG = {
    "response_strategy": "smart",
    "admin_ids": [],
    "language": "pt-br"
}

# Prompts
DEFAULT_PROMPT = f"""Você é {BOT_NAME}, um assistente de IA no Telegram. Siga estas regras:
1. Responda imediatamente quando mencionado com @
2. Seja conciso (1-2 frases) em respostas não direcionadas
3. Corrija informações erradas educadamente
4. Use tom casual mas informativo
5. Mantenha o contexto da conversa
6. Use emojis quando apropriado 👋🤖
7. Se não souber, diga "Não tenho essa informação"
8. Para perguntas complexas, peça detalhes"""

CORRECTION_PROMPT = """🔍 Correção: Detectei um pequeno engano...
A informação correta é:"""
