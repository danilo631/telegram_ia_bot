# database.py
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime
from config import (
    MESSAGES_FILE,
    USERS_FILE,
    CONFIG_FILE,
    GROUPS_FILE,
    MAX_MESSAGES_STORED,
    DEFAULT_CONFIG
)
import aiofiles
import asyncio
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.initialized = False

    async def initialize(self):
        """Inicializa o banco de dados"""
        if not self.initialized:
            await self._ensure_files_exist()
            self.initialized = True

    async def _ensure_files_exist(self):
        """Garante que todos os arquivos existam"""
        defaults = {
            MESSAGES_FILE: [],
            USERS_FILE: [],
            CONFIG_FILE: DEFAULT_CONFIG,
            GROUPS_FILE: {}
        }
        
        for file, default in defaults.items():
            if not file.exists():
                async with aiofiles.open(file, 'w') as f:
                    await f.write(json.dumps(default, indent=2))
                logger.info(f"Criado arquivo {file.name}")

    async def _load_data(self, file: Path) -> Union[List, Dict]:
        """Carrega dados de um arquivo"""
        try:
            async with aiofiles.open(file, 'r') as f:
                content = await f.read()
                return json.loads(content) if content else ({} if file == GROUPS_FILE else [])
        except Exception as e:
            logger.error(f"Erro ao carregar {file.name}: {str(e)}")
            return {} if file == GROUPS_FILE else []

    async def _save_data(self, file: Path, data: Union[List, Dict]):
        """Salva dados em um arquivo"""
        try:
            async with aiofiles.open(file, 'w') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Erro ao salvar em {file.name}: {str(e)}")

    async def save_message(self, chat_id: int, user_id: int, username: str, text: str, is_bot: bool = False):
        """Salva uma mensagem no histórico"""
        try:
            messages = await self._load_data(MESSAGES_FILE)
            
            message = {
                "timestamp": datetime.now().isoformat(),
                "chat_id": chat_id,
                "user_id": user_id,
                "username": username,
                "text": text,
                "is_bot": is_bot,
                "accurate": True
            }
            
            messages.append(message)
            await self._save_data(MESSAGES_FILE, messages[-MAX_MESSAGES_STORED:])
            
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {str(e)}")

    async def save_user(self, user_id: int, username: str):
        """Salva ou atualiza um usuário"""
        try:
            users = await self._load_data(USERS_FILE)
            
            # Verificar se usuário já existe
            user_exists = False
            for user in users:
                if user['user_id'] == user_id:
                    user['username'] = username
                    user['last_seen'] = datetime.now().isoformat()
                    user['message_count'] = user.get('message_count', 0) + 1
                    user_exists = True
                    break
            
            if not user_exists:
                users.append({
                    "user_id": user_id,
                    "username": username,
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                    "message_count": 1
                })
            
            await self._save_data(USERS_FILE, users)
            
        except Exception as e:
            logger.error(f"Erro ao salvar usuário: {str(e)}")

    async def save_group(self, chat_id: int, title: str, creator_id: int, admins: list = None):
        """Salva ou atualiza informações de um grupo"""
        try:
            groups = await self._load_data(GROUPS_FILE)
            
            if chat_id not in groups:
                groups[chat_id] = {
                    "title": title,
                    "creator_id": creator_id,
                    "admins": admins or [],
                    "created_at": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat()
                }
            else:
                groups[chat_id]['title'] = title
                groups[chat_id]['last_activity'] = datetime.now().isoformat()
                if admins:
                    groups[chat_id]['admins'] = admins
            
            await self._save_data(GROUPS_FILE, groups)
            
        except Exception as e:
            logger.error(f"Erro ao salvar grupo: {str(e)}")

    async def get_conversation_context(self, chat_id: int, limit: int = 10) -> str:
        """Obtém o contexto da conversa"""
        try:
            messages = await self._load_data(MESSAGES_FILE)
            chat_messages = [m for m in messages if m['chat_id'] == chat_id][-limit:]
            return "\n".join([f"{m['username']}: {m['text']}" for m in chat_messages])
        except Exception as e:
            logger.error(f"Erro ao obter contexto: {str(e)}")
            return ""

    async def get_last_reply(self, chat_id: int) -> Optional[Dict]:
        """Obtém a última resposta do bot"""
        try:
            messages = await self._load_data(MESSAGES_FILE)
            bot_messages = [m for m in messages if m['chat_id'] == chat_id and m['is_bot']]
            return bot_messages[-1] if bot_messages else None
        except Exception as e:
            logger.error(f"Erro ao obter última resposta: {str(e)}")
            return None

    async def get_config(self) -> Dict:
        """Obtém a configuração atual"""
        return await self._load_data(CONFIG_FILE)

    async def update_config(self, config: Dict):
        """Atualiza a configuração"""
        await self._save_data(CONFIG_FILE, config)

    async def get_group_info(self, chat_id: int) -> Optional[Dict]:
        """Obtém informações de um grupo"""
        groups = await self._load_data(GROUPS_FILE)
        return groups.get(str(chat_id))

    async def count_messages(self) -> Dict[int, int]:
        """Conta mensagens por chat"""
        try:
            messages = await self._load_data(MESSAGES_FILE)
            counts = {}
            for msg in messages:
                counts[msg['chat_id']] = counts.get(msg['chat_id'], 0) + 1
            return counts
        except Exception as e:
            logger.error(f"Erro ao contar mensagens: {str(e)}")
            return {}

# Instância global
db = Database()

# Funções de interface
async def save_message(*args, **kwargs):
    return await db.save_message(*args, **kwargs)

async def save_user(*args, **kwargs):
    return await db.save_user(*args, **kwargs)

async def save_group(*args, **kwargs):
    return await db.save_group(*args, **kwargs)

async def get_conversation_context(*args, **kwargs):
    return await db.get_conversation_context(*args, **kwargs)

async def get_last_reply(*args, **kwargs):
    return await db.get_last_reply(*args, **kwargs)

async def get_config():
    return await db.get_config()

async def update_config(config: Dict):
    return await db.update_config(config)

async def get_group_info(*args, **kwargs):
    return await db.get_group_info(*args, **kwargs)

async def count_messages():
    return await db.count_messages()
