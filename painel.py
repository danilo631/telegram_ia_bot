# painel.py
import gradio as gr
from database import contar_mensagens_por_chat

def painel():
    dados = contar_mensagens_por_chat()
    if not dados:
        return "Nenhuma mensagem registrada ainda."
    return "\n".join([f"Grupo {chat_id}: {qtd} mensagens" for chat_id, qtd in dados])

def iniciar_painel():
    iface = gr.Interface(fn=painel, inputs=[], outputs="text", title="📊 Painel do Bot Telegram IA")
    iface.launch(server_port=7860)
