# -*- coding: utf-8 -*-
import os

from taipy.gui import notify, Markdown
import pandas as pd
from utils.ppt import create_presentation
from postgrest import SyncPostgrestClient, DEFAULT_POSTGREST_CLIENT_HEADERS


def on_checkbox_change(state, linha):
    global linhas_selecionadas
    if state:
        linhas_selecionadas.append(linha["id"])
    else:
        linhas_selecionadas.remove(linha["id"])


def return_dados():
    tbl = None
    try:
        pg_headers = DEFAULT_POSTGREST_CLIENT_HEADERS.copy()
        pg_headers["Authorization"] = f"Bearer {os.getenv("PGRST_TKN")}"
        supabase: SyncPostgrestClient = SyncPostgrestClient(
            os.getenv("PGRST_URL"), schema=os.getenv("PGRST_SCH"), headers=pg_headers
        )
        tbl = supabase.from_("questoes_gemini").select("*").order("id").execute()
        df = pd.DataFrame(tbl.data)
        df["label"] = "Questão " + df["id"].astype(str)
        df["selecionado"] = False
        df.set_index("id", inplace=True)
        df.index.name = "index"
        supabase.aclose()
    except:
        pass
    return df


# Definição de Variável
dados = return_dados()
link = ""
content = None
download_active = False
display_resultado = None
display_index = None
display_area = None
display_label = None
linhas_selecionadas = []  # Armazena os IDs das linhas selecionadas


def refresh_dados(state):
    state.dados = return_dados()


def exportar_ppt(state):
    create_presentation(state.dados, "template/Questoes_Desafio.pptx", "questoes.pptx")
    state.content = open("questoes.pptx", "rb").read()
    state.download_active = True
    state.link = "questoes.pptx"
    notify(state, "success", "Powerpoint Gerado!")


def download_start(state):
    state.download_active = False


def delete_questao(state, var_name, payload):
    pg_headers = DEFAULT_POSTGREST_CLIENT_HEADERS.copy()
    pg_headers["Authorization"] = f"Bearer {os.getenv("PGRST_TKN")}"
    supabase: SyncPostgrestClient = SyncPostgrestClient(
        os.getenv("PGRST_URL"), schema=os.getenv("PGRST_SCH"), headers=pg_headers
    )
    data = (
        supabase.from_("questoes_gemini").delete().eq("id", payload["index"]).execute()
    )
    supabase.aclose()
    state.dados = return_dados()
    state.download_active = False
    notify(state, "success", "Questão removida!")


def show_resultado(state, var_name, payload):
    state.display_index = payload["index"]
    state.display_resultado = state.dados["resultado"][payload["index"]]
    state.display_area = state.dados["area"][payload["index"]]
    state.display_label = state.dados["label"][payload["index"]]


def salvar_questao(state):
    pg_headers = DEFAULT_POSTGREST_CLIENT_HEADERS.copy()
    pg_headers["Authorization"] = f"Bearer {os.getenv("PGRST_TKN")}"
    supabase: SyncPostgrestClient = SyncPostgrestClient(
        os.getenv("PGRST_URL"), schema=os.getenv("PGRST_SCH"), headers=pg_headers
    )
    data = (
        supabase.from_("questoes_gemini")
        .update({"resultado": state.display_resultado})
        .eq("id", state.display_index)
        .execute()
    )
    supabase.aclose()
    state.dados = return_dados()
    state.download_active = False
    notify(state, "success", "Questão alterada!")


# Definição Pagina
tbl_q_md = Markdown(
    """<|container|
        
# Lista de Questões Geradas

<|layout|columns=1fr|gap=5px|class_name=card|
<|c1|
<center><|Atualizar|button|on_action=refresh_dados|> <|Exportar|button|on_action=exportar_ppt|> 
<|{content}|file_download|label=Download|name={link}|active={download_active}|on_action=download_start|></center>
|>
|>
<|layout|columns=475px 1fr|gap=5px|class_name=card|
<|c2|
<|{dados}|table|page_size=15|columns=label;nivel;tipo|class_name=fullwidth|editable=True|on_delete=delete_questao|on_action=show_resultado|>
|>
<|c3|
<|{display_label}|text|><br/>
<|{display_area}|text|><br/>
<|{display_resultado}|input|label="Questão"|multiline=true|class_name=fullwidth|>
<br/>
<center><|Salvar|button|on_action=salvar_questao|></center>
|>
|>
|>
"""
)
