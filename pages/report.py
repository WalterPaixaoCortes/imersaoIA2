# -*- coding: utf-8 -*-
import os
from taipy.gui import notify, Markdown
from postgrest import SyncPostgrestClient, DEFAULT_POSTGREST_CLIENT_HEADERS
import pandas as pd


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
        supabase.aclose()
    except:
        pass
    return df


# Definição de Variável
dados = return_dados()
areas = dados.groupby("area")["id"].count().reset_index()
areas.rename(columns={"id": "contagem_ids"}, inplace=True)
tipos = dados.groupby("tipo")["id"].count().reset_index()
tipos.rename(columns={"id": "contagem_ids"}, inplace=True)


def refresh_dados(state):
    state.dados = return_dados()
    state.areas = state.dados.groupby("area")["id"].count().reset_index()
    state.areas.rename(columns={"id": "contagem_ids"}, inplace=True)
    state.tipos = state.dados.groupby("tipo")["id"].count().reset_index()
    state.tipos.rename(columns={"id": "contagem_ids"}, inplace=True)


# Definição Pagina
sum_q_md = Markdown(
    """<|container|
        
# Dashboard

<center><|Atualizar|button|on_action=refresh_dados|></center>

<|layout|columns=1fr 1fr|gap=5px|class_name=card|
<|c1|
<|{areas}|chart|type=pie|values=contagem_ids|labels=area|>
|>
<|c2|
<|{tipos}|chart|type=pie|values=contagem_ids|labels=tipo|>
|>
|>
|>
"""
)
