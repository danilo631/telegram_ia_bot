# painel.py
from database import count_messages, get_conversation_context, get_group_info
import gradio as gr
import asyncio
from config import BOT_NAME
import logging

logger = logging.getLogger(__name__)

async def generate_report():
    """Gera relatório de atividades"""
    try:
        message_counts = await count_messages()
        if not message_counts:
            return "Nenhuma mensagem registrada ainda."
        
        report = [f"# 📊 Relatório do {BOT_NAME}\n"]
        
        for chat_id, count in message_counts.items():
            group_info = await get_group_info(chat_id)
            group_name = group_info['title'] if group_info else f"Chat {chat_id}"
            
            context = await get_conversation_context(chat_id, 3)
            
            report.append(
                f"\n## 💬 {group_name} (ID: {chat_id})\n"
                f"- 📝 Mensagens totais: {count}\n"
                f"- 🕒 Últimas mensagens:\n{context}\n"
            )
        
        return "\n".join(report)
    
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return "⚠️ Erro ao gerar relatório."

def start_panel():
    """Inicia o painel de controle"""
    try:
        with gr.Blocks(title=f"Painel do {BOT_NAME}") as interface:
            gr.Markdown(f"# 🛠️ Painel de Controle - {BOT_NAME}")
            
            with gr.Row():
                refresh_btn = gr.Button("Atualizar Relatório", variant="primary")
                clear_btn = gr.Button("Limpar Dados", variant="stop")
            
            report_output = gr.Markdown()
            
            refresh_btn.click(
                fn=generate_report,
                outputs=report_output
            )
            
            clear_btn.click(
                fn=lambda: "⚠️ Função não implementada",
                outputs=report_output
            )
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
    except Exception as e:
        logger.error(f"Erro no painel: {str(e)}")

if __name__ == "__main__":
    start_panel()
