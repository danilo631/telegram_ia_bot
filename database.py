# database.py
import sqlite3
from config import DB_FILE

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    usuario TEXT,
    texto TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

def salvar_mensagem(chat_id, usuario, texto):
    cursor.execute("INSERT INTO mensagens (chat_id, usuario, texto) VALUES (?, ?, ?)", (chat_id, usuario, texto))
    conn.commit()

def obter_ultimas_mensagens(chat_id, limite=100):
    cursor.execute("SELECT usuario, texto FROM mensagens WHERE chat_id = ? ORDER BY id DESC LIMIT ?", (chat_id, limite))
    mensagens = cursor.fetchall()
    return [f"{usuario}: {texto}" for usuario, texto in reversed(mensagens)]

def contar_mensagens_por_chat():
    cursor.execute("SELECT chat_id, COUNT(*) FROM mensagens GROUP BY chat_id")
    return cursor.fetchall()
