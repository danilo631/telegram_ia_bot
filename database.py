# database.py
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime
from config import MESSAGES_FILE, USERS_FILE, MAX_CONTEXT_LENGTH, MAX_HISTORY_MESSAGES, MAX_MESSAGES_STORED
import logging
import aiofiles
import asyncio

logger = logging.getLogger(__name__)

async def initialize_database():
    """Inicializa os arquivos JSON se não existirem"""
    for file in [MESSAGES_FILE, USERS_FILE]:
        if not file.exists():
            async with aiofiles.open(file, 'w') as f:
                await f.write('[]')
            logger.info(f"Criado arquivo {file.name}")

async def _load_data(file_path: Path) -> List[Dict]:
    """Carrega dados de um arquivo JSON"""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content) if content else []
    except Exception as e:
        logger.error(f"Erro ao carregar {file_path.name}: {str(e)}")
        return []

async def _save_data(file_path: Path, data: List[Dict]):
    """Salva dados em um arquivo JSON"""
    try:
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"Erro ao salvar em {file_path.name}: {str(e)}")

async def salvar_mensagem(chat_id: int, user_id: int, user_name: str, texto: str, is_bot: bool = False):
    """Salva uma mensagem no histórico"""
    try:
        messages = await _load_data(MESSAGES_FILE)
        
        new_message = {
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id,
            "user_id": user_id,
            "user_name": user_name,
            "text": texto,
            "is_bot": is_bot
        }
        
        messages.append(new_message)
        # Mantém apenas as mensagens mais recentes
        await _save_data(MESSAGES_FILE, messages[-MAX_MESSAGES_STORED:])
        
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem: {str(e)}")

async def salvar_usuario(user_id: int, user_name: str) -> bool:
    """Salva ou atualiza um usuário"""
    try:
        users = await _load_data(USERS_FILE)
        
        # Atualiza se já existe, adiciona se não existe
        user_exists = False
        for user in users:
            if user['user_id'] == user_id:
                user['user_name'] = user_name
                user['last_seen'] = datetime.now().isoformat()
                user['message_count'] = user.get('message_count', 0) + 1
                user_exists = True
                break
        
        if not user_exists:
            users.append({
                "user_id": user_id,
                "user_name": user_name,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "message_count": 1
            })
        
        await _save_data(USERS_FILE, users)
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar usuário: {str(e)}")
        return False

async def usuario_existe(user_id: int) -> bool:
    """Verifica se um usuário existe no banco de dados"""
    try:
        users = await _load_data(USERS_FILE)
        return any(user['user_id'] == user_id for user in users)
    except Exception as e:
        logger.error(f"Erro ao verificar usuário: {str(e)}")
        return False

async def obter_contexto_conversa(chat_id: int, limite: int = MAX_HISTORY_MESSAGES) -> str:
    """Obtém o contexto da conversa para um chat específico"""
    try:
        messages = await _load_data(MESSAGES_FILE)
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
        
        return "\n".join(contexto) if contexto else "Nenhum contexto disponível."
    
    except Exception as e:
        logger.error(f"Erro ao obter contexto: {str(e)}")
        return "Erro ao carregar contexto."

async def contar_mensagens_por_chat() -> Dict[int, int]:
    """Conta mensagens por chat"""
    try:
        messages = await _load_data(MESSAGES_FILE)
        counts = {}
        
        for msg in messages:
            chat_id = msg['chat_id']
            counts[chat_id] = counts.get(chat_id, 0) + 1
            
        return counts
        
    except Exception as e:
        logger.error(f"Erro ao contar mensagens: {str(e)}")
        return {}
