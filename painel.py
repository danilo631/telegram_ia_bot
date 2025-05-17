# painel.py
from database import contar_mensagens_por_chat, obter_contexto_conversa
import gradio as gr
from typing import Dict

def gerar_relatorio():
    dados = contar_mensagens_por_chat()
    if not dados:
        return "Nenhuma mensagem registrada ainda."
    
    relatorio = ["📊 Relatório de Atividade do Bot"]
    for chat_id, qtd in dados.items():
        contexto = obter_contexto_conversa(chat_id, limite=5)
        relatorio.append(
            f"\n\n💬 Grupo {chat_id}:\n"
            f"📝 Total de mensagens: {qtd}\n"
            f"Últimas mensagens:\n{contexto}"
        )
    
    return "\n".join(relatorio)

def iniciar_painel():
    iface = gr.Interface(
        fn=gerar_relatorio,
        inputs=[],
        outputs="text",
        title="🤖 Painel de Controle do Bot",
        description="Relatório de atividade e interações do bot"
    )
    iface.launch(server_port=7860, share=False)
