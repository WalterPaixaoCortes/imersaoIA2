# -*- coding: utf-8 -*-
import os
from taipy.gui import Gui, notify, Markdown
from supabase import create_client, Client

import utils.oai as genai
import utils.config as config


def send_database(state, id, action):
    try:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        tbl = supabase.table("questoes_gemini")
        tbl.insert(
            {
                "area": state.area,
                "tipo": state.tipo,
                "nivel": state.nivel,
                "prompt": state.prompt,
                "resultado": state.resultado,
            }
        ).execute()
        notify(state, "sucesso", "Questão salva!")
        state.salvar = False
    except:
        notify(state, "error", "Erro ao salvar a questão")


def send_question(state, id, action):
    state.resultado = "Waiting ..."
    resultado = None

    gemini = genai.Openai()
    gemini.set_key(os.getenv("OAI_API_KEY"))
    resultado = gemini.complete(
        state.prompt.format(state.pergunta, state.gabarito, state.resposta)
    )
    if resultado:
        state.resultado = resultado
        notify(state, "success", "Questão criada!")
    else:
        state.resultado = "Erro ao utilizar o Gemini. Verifique o Log"
        notify(state, "success", "Questão criada!")


# Definição de Variável
pergunta = ""
gabarito = ""
resposta = ""
prompt = """
Dada a pergunta:
{0}

e o gabarito de resposta:
{1}

verifique se a resposta:
{2}
está correta segundo  o gabarito.

A classificação deve ser feita usando critérios:
- precisão
- alinhamento
- relevância
Classifique a resposta com uma nota entre 1 e 10.
Dê a nota e explique o que faltou para o 10."""
resultado = ""

# Definição Pagina
dis_q_md = Markdown(
    """<|container|
    
# Correção de Questões Dissertativas

<|{pergunta}|input|label=Pergunta|class_name=fullwidth|>

<|layout|columns=1fr 1fr|gap=5px|class_name=card|
<|c1|
**Gabarito**
|>
<|c2|
**Resposta**
|>
<|c3|
<|{gabarito}|input|multiline|label=Gabarito|class_name=fullwidth|>
|>
<|c4|
<|{resposta}|input|multiline|label=Resposta|class_name=fullwidth|>
|>
|>
---
<br/>
<|{prompt}|input|multiline|label=Prompt|class_name=fullwidth|>
<br />
<center><|Gerar Questão|button|on_action=send_question|></center>
<br/>
<br/>
<|{resultado}|input|multiline|label=Resultado|class_name=fullwidth|>
|>
"""
)
