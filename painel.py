# painel.py
from database import contar_mensagens_por_chat, obter_contexto_conversa
import gradio as gr
import asyncio
from typing import Dict
import logging

logger = logging.getLogger(__name__)

async def gerar_relatorio():
    """Gera um relatório completo da atividade do bot"""
    try:
        dados = await contar_mensagens_por_chat()
        if not dados:
            return "Nenhuma mensagem registrada ainda."
        
        relatorio = ["📊 *Relatório Completo do Bot*"]
        
        for chat_id, qtd in dados.items():
            contexto = await obter_contexto_conversa(chat_id, limite=5)
            relatorio.append(
                f"\n\n💬 *Grupo {chat_id}:*\n"
                f"✉️ *Mensagens totais:* {qtd}\n"
                f"🔍 *Últimas mensagens:*\n{contexto}"
            )
        
        return "\n".join(relatorio)
    
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return "⚠️ Erro ao gerar relatório."

def iniciar_painel():
    """Inicia a interface do painel de controle"""
    try:
        iface = gr.Interface(
            fn=gerar_relatorio,
            inputs=[],
            outputs="markdown",
            title="🤖 Painel de Controle do Bot Telegram",
            description="Visualize a atividade e interações do bot em tempo real",
            allow_flagging="never"
        )
        
        iface.launch(
            server_port=7860,
            server_name="0.0.0.0",
            share=False,
            show_error=True
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar painel: {str(e)}")
