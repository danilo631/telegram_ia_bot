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
import aiofiles
import asyncio
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.initialized = False

    async def initialize(self):
        if not self.initialized:
            await self._ensure_files_exist()
            self.initialized = True

    async def _ensure_files_exist(self):
        for file, default in [
            (MESSAGES_FILE, []),
            (USERS_FILE, []),
            (CONFIG_FILE, DEFAULT_CONFIG)
        ]:
            if not file.exists():
                async with aiofiles.open(file, 'w') as f:
                    await f.write(json.dumps(default, indent=2))

    async def _load_data(self, file: Path) -> Union[List, Dict]:
        async with aiofiles.open(file, 'r') as f:
            return json.loads(await f.read())

    async def _save_data(self, file: Path, data: Union[List, Dict]):
        async with aiofiles.open(file, 'w') as f:
            await f.write(json.dumps(data, indent=2))

    async def salvar_mensagem(self, chat_id: int, user_id: int, user_name: str, text: str, is_bot: bool = False):
        messages = await self._load_data(MESSAGES_FILE)
        messages.append({
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id,
            "user_id": user_id,
            "user_name": user_name,
            "text": text,
            "is_bot": is_bot
        })
        await self._save_data(MESSAGES_FILE, messages[-MAX_MESSAGES_STORED:])

    async def get_config(self) -> Dict:
        return await self._load_data(CONFIG_FILE)

    async def update_config(self, config: Dict):
        await self._save_data(CONFIG_FILE, config)

# Instância global
db = Database()

# Funções de interface
async def salvar_mensagem(*args, **kwargs):
    return await db.salvar_mensagem(*args, **kwargs)

async def get_config():
    return await db.get_config()

async def update_config(config: Dict):
    return await db.update_config(config)
