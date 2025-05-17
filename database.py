# database.py
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime
from config import (
    MESSAGES_FILE,
    USERS_FILE,
    CONFIG_FILE,
    MAX_MESSAGES_STORED,
    DEFAULT_CONFIG
)
import logging
import aiofiles
import asyncio

logger = logging.getLogger(__name__)

async def initialize_database():
    """Inicializa todos os arquivos JSON necessários"""
    files = {
        MESSAGES_FILE: [],
        USERS_FILE: [],
        CONFIG_FILE: DEFAULT_CONFIG
    }
    
    for file, default in files.items():
        if not file.exists():
            async with aiofiles.open(file, 'w') as f:
                await f.write(json.dumps(default, indent=2))
            logger.info(f"Arquivo {file.name} criado")

async def _load_data(file_path: Path) -> Union[List, Dict]:
    """Carrega dados de um arquivo JSON"""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content) if content else []
    except Exception as e:
        logger.error(f"Erro ao carregar {file_path.name}: {str(e)}")
        return [] if file_path != CONFIG_FILE else {}

async def _save_data(file_path: Path, data: Union[List, Dict]):
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
            "is_bot": is_bot,
            "accurate": True
        }
        
        messages.append(new_message)
        await _save_data(MESSAGES_FILE, messages[-MAX_MESSAGES_STORED:])
        
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem: {str(e)}")

async def salvar_usuario(user_id: int, user_name: str) -> bool:
    """Salva ou atualiza um usuário"""
    try:
        users = await _load_data(USERS_FILE)
        
        for user in users:
            if user['user_id'] == user_id:
                user['user_name'] = user_name
                user['last_seen'] = datetime.now().isoformat()
                user['message_count'] = user.get('message_count', 0) + 1
                await _save_data(USERS_FILE, users)
                return True
        
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
    """Verifica se um usuário existe"""
    users = await _load_data(USERS_FILE)
    return any(user['user_id'] == user_id for user in users)

async def obter_contexto_conversa(chat_id: int, limite: int = 10) -> str:
    """Obtém o contexto da conversa"""
    messages = await _load_data(MESSAGES_FILE)
    chat_messages = [
        msg for msg in messages 
        if msg['chat_id'] == chat_id
    ][-limite:]
    
    return "\n".join(
        f"{msg['user_name']}: {msg['text']}" 
        for msg in chat_messages
    )

async def get_last_reply(chat_id: int) -> Optional[Dict]:
    """Obtém a última resposta do bot no chat"""
    messages = await _load_data(MESSAGES_FILE)
    bot_messages = [
        msg for msg in messages 
        if msg['chat_id'] == chat_id and msg['is_bot']
    ]
    return bot_messages[-1] if bot_messages else None

async def get_config() -> Dict:
    """Obtém a configuração atual"""
    return await _load_data(CONFIG_FILE)

async def update_config(config: Dict):
    """Atualiza a configuração"""
    await _save_data(CONFIG_FILE, config)

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
