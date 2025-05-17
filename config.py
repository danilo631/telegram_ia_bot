# config.py
import os
from pathlib import Path

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

# Configurações de contexto
MAX_CONTEXT_LENGTH = 1500  # Número máximo de caracteres para o contexto
MAX_HISTORY_MESSAGES = 20  # Número máximo de mensagens no histórico
