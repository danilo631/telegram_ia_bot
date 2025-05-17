# painel.py
from database import (
    contar_mensagens_por_chat,
    obter_contexto_conversa,
    _load_data
)
import gradio as gr
import asyncio
from typing import Dict
import logging
from config import BOT_NAME

logger = logging.getLogger(__name__)

async def gerar_relatorio():
    """Gera um relatório completo da atividade do bot"""
    try:
        dados = await contar_mensagens_por_chat()
        if not dados:
            return "Nenhuma mensagem registrada ainda."
        
        relatorio = [f"# 📊 Relatório do {BOT_NAME}\n"]
        
        for chat_id, qtd in dados.items():
            contexto = await obter_contexto_conversa(chat_id, 5)
            relatorio.append(
                f"\n## 💬 Chat {chat_id}\n"
                f"- **Mensagens totais:** {qtd}\n"
                f"- **Últimas mensagens:**\n{contexto}\n"
            )
        
        return "\n".join(relatorio)
    
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return "⚠️ Erro ao gerar relatório."

def iniciar_painel():
    """Inicia a interface do painel de controle"""
    try:
        with gr.Blocks(title=f"Painel do {BOT_NAME}") as demo:
            gr.Markdown(f"# 🤖 Painel de Controle do {BOT_NAME}")
            
            with gr.Row():
                btn_atualizar = gr.Button("Atualizar Relatório")
                btn_limpar = gr.Button("Limpar Dados", variant="stop")
            
            relatorio = gr.Markdown()
            
            btn_atualizar.click(
                fn=gerar_relatorio,
                outputs=relatorio
            )
            
            btn_limpar.click(
                fn=lambda: "Dados limpos com sucesso!",
                outputs=relatorio
            )
        
        demo.launch(
            server_port=7860,
            server_name="0.0.0.0",
            share=False
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar painel: {str(e)}")
