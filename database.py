# database.py
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from config import MESSAGES_FILE, USERS_FILE, MAX_CONTEXT_LENGTH, MAX_HISTORY_MESSAGES
import logging

logger = logging.getLogger(__name__)

def _load_data(file_path: Path) -> List[Dict]:
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Erro ao carregar dados de {file_path}: {e}")
        return []

def _save_data(file_path: Path, data: List[Dict]):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Erro ao salvar dados em {file_path}: {e}")

def salvar_mensagem(chat_id: int, user_id: int, user_name: str, texto: str, is_bot: bool = False):
    try:
        messages = _load_data(MESSAGES_FILE)
        
        new_message = {
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id,
            "user_id": user_id,
            "user_name": user_name,
            "text": texto,
            "is_bot": is_bot
        }
        
        messages.append(new_message)
        _save_data(MESSAGES_FILE, messages[-1000:])  # Mantém apenas as 1000 mensagens mais recentes
        
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem: {e}")

def salvar_usuario(user_id: int, user_name: str):
    try:
        users = _load_data(USERS_FILE)
        
        # Verifica se o usuário já existe
        user_exists = any(u['user_id'] == user_id for u in users)
        
        if not user_exists:
            new_user = {
                "user_id": user_id,
                "user_name": user_name,
                "first_seen": datetime.now().isoformat(),
                "message_count": 0
            }
            users.append(new_user)
            _save_data(USERS_FILE, users)
            
    except Exception as e:
        logger.error(f"Erro ao salvar usuário: {e}")

def obter_contexto_conversa(chat_id: int, limite: int = MAX_HISTORY_MESSAGES) -> str:
    try:
        messages = _load_data(MESSAGES_FILE)
        chat_messages = [
            msg for msg in messages 
            if msg['chat_id'] == chat_id and not msg['is_bot']
        ][-limite:]
        
        contexto = []
        current_length = 0
        
        for msg in reversed(chat_messages):
            msg_text = f"{msg['user_name']}: {msg['text']}"
            if current_length + len(msg_text) > MAX_CONTEXT_LENGTH:
                break
            contexto.insert(0, msg_text)
            current_length += len(msg_text)
        
        return "\n".join(contexto)
    
    except Exception as e:
        logger.error(f"Erro ao obter contexto: {e}")
        return ""

def contar_mensagens_por_chat() -> Dict[int, int]:
    try:
        messages = _load_data(MESSAGES_FILE)
        counts = {}
        
        for msg in messages:
            chat_id = msg['chat_id']
            counts[chat_id] = counts.get(chat_id, 0) + 1
            
        return counts
        
    except Exception as e:
        logger.error(f"Erro ao contar mensagens: {e}")
        return {}
