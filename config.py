# config.py
from pathlib import Path
import os

# Configurações básicas
BOT_NAME = "SuperAI"
BOT_USERNAME = "SuperAi148_bot"  # Atualize com seu username real

# Tokens e configurações da API
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

# Configurações de contexto
MAX_CONTEXT_LENGTH = 2000
MAX_HISTORY_MESSAGES = 15
MAX_MESSAGES_STORED = 1000

# Estratégia de resposta
RESPONSE_STRATEGY = "smart"  # smart, always, mention-only

# Palavras-chave que ativam o bot
BOT_TRIGGERS = [
    "superai",
    "assistente",
    "ajuda",
    "dúvida",
    "pergunta",
    "sabe",
    "como funciona"
]

# Prompt do sistema
DEFAULT_PROMPT = """Você é {bot_name}, um assistente de IA em um grupo do Telegram. Siga estas regras:

1. Quando mencionado diretamente (@), responda imediatamente e completamente
2. Para perguntas diretas, responda de forma concisa
3. Se detectar informações incorretas, corrija educadamente
4. Use tom casual mas informativo
5. Mantenha o contexto da conversa
6. Use emojis quando apropriado
7. Se não souber, diga que não sabe
8. Respostas curtas (1-2 frases) para mensagens não direcionadas

Contexto atual:"""

CORRECTION_PROMPT = """Você detectou uma informação potencialmente incorreta. 
Corrija de forma educada e forneça a informação correta com fonte se possível:"""
