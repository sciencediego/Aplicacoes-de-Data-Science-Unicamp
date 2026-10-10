# Cadastro de Pacientes - versão GRADIO

import os
from datetime import datetime

import gradio as gr
import pandas as pd

ARQUIVO_CSV = "pacientes.csv"
COLUNAS = ["timestamp", "nome", "idade", "convenio", "prioridade", "motivo"]
CONVENIOS = ["Particular", "Unimed", "Bradesco Saude", "SulAmerica", "Outro"]


def ler_ultimos(n=5):
    #Lê o CSV (se existir) e devolve os n últimos cadastros.
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV).tail(n)
    return pd.DataFrame(columns=COLUNAS)


def cadastrar_paciente(nome, idade, convenio, prioridade, motivo):
    # 1) Validação: não grava informações incorretas no arquivo
    if not nome or not nome.strip():
        return "Informe o nome do paciente.", ler_ultimos(), gr.update(), gr.update(), gr.update()
    if idade is None or not (0 <= idade <= 120):
        return "Idade deve estar entre 0 e 120.", ler_ultimos(), gr.update(), gr.update(), gr.update()
    if not convenio:
        return "Selecione o convênio.", ler_ultimos(), gr.update(), gr.update(), gr.update()

    # 2) Montagem da linha
    linha = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome.strip(),
        "idade": int(idade),
        "convenio": convenio,
        "prioridade": int(prioridade),
        "motivo": (motivo or "").strip(),
    }
    novo = pd.DataFrame([linha])

    # 3) Grava: cria com cabeçalho na 1ª vez, depois só acrescenta (append)
    if os.path.exists(ARQUIVO_CSV):
        novo.to_csv(ARQUIVO_CSV, mode="a", header=False, index=False)
    else:
        novo.to_csv(ARQUIVO_CSV, mode="w", header=True, index=False)

    # 4) Devolve: mensagem, tabela atualizada e campos limpos
    return "✅ Paciente cadastrado com sucesso!", ler_ultimos(), "", None, ""


with gr.Blocks(title="Cadastro de Pacientes") as demo:
    gr.Markdown("## Cadastro de Pacientes")

    # Layout em coluna única para celular
    nome = gr.Textbox(label="Nome do paciente")
    idade = gr.Number(label="Idade", precision=0, minimum=0, maximum=120)
    convenio = gr.Dropdown(CONVENIOS, label="Convênio")
    prioridade = gr.Slider(1, 5, value=1, step=1,
                           label="Prioridade do atendimento (5 = urgente)")
    motivo = gr.Textbox(label="Motivo da consulta / observações", lines=3)
    botao = gr.Button("Cadastrar", variant="primary")

    saida_msg = gr.Textbox(label="Status", interactive=False)
    tabela = gr.Dataframe(label="Últimos pacientes cadastrados", value=ler_ultimos())

    botao.click(
        cadastrar_paciente,
        inputs=[nome, idade, convenio, prioridade, motivo],
        outputs=[saida_msg, tabela, nome, idade, motivo],
    )

if __name__ == "__main__":
    demo.launch()
