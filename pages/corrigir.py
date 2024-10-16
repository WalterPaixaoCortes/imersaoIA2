import os
import shutil
import subprocess
from taipy.gui import Markdown
import pandas as pd


gabarito = ""
questoes = ""
resultado = ""
nome = ""
dados = ""
download_file = "resultado.xlsx"
download_content = ""
download_ativo = False


def download_start(state):
    state.download_ativo = False


def validar(gabarito: str, folder_avaliacao: str):

    resultados = []

    # Roda o gabarito
    result = subprocess.run(["python", gabarito], capture_output=True, text=True)
    gabarito_output = result.stdout

    for item in os.listdir(folder_avaliacao):
        if item.endswith(".py") and not item.startswith("gabarito"):
            result = subprocess.run(
                ["python", os.path.join(folder_avaliacao, item)],
                capture_output=True,
                text=True,
            )
            output = result.stdout

            resultados.append(
                {
                    "gabarito": gabarito_output,
                    "output": output,
                    "arquivo": item,
                    "status": "OK" if gabarito_output == output else "ERRO",
                }
            )
    return resultados


def evaluate(state, id, action):
    state.download_ativo = False
    if (
        os.path.exists(state.gabarito)
        and os.path.exists(state.questoes)
        and state.nome != ""
    ):
        if os.path.exists(state.nome):
            shutil.rmtree(state.nome)
        os.mkdir(state.nome)
        os.system(f"unzip {state.questoes} -d {state.nome}")
        os.system(f"cp {state.gabarito} .")
        if state.dados != "":
            os.system(f"cp {state.dados} .")

        gabarito = os.path.basename(state.gabarito)
        folder_avaliacao = state.nome
        state.resultado = "Avaliando ..." + "\n" + gabarito + "\n" + folder_avaliacao
        resultado = validar(gabarito, folder_avaliacao)
        state.resultado += "\n Finalizado!"
        if state.dados != "":
            os.remove(os.path.basename(state.dados))

        os.remove(os.path.basename(state.gabarito))

        os.remove(state.questoes)
        os.remove(state.gabarito)
        os.remove(state.dados)

        if len(resultado) > 0:
            df = pd.DataFrame(resultado)
            df.to_excel(
                f"{state.nome}/{state.nome}.xlsx", sheet_name="resultados", index=False
            )
            state.download_content = open(
                f"{state.nome}/{state.nome}.xlsx", "rb"
            ).read()
            state.download_ativo = True
    else:
        state.resultado = "Erro: Arquivos não encontrados!"


cor_q_md = Markdown(
    """<|container|
    
# Corrigir Questões de Código

<|{nome}|input|label=Nome|class_name=fullwidth|>

<|layout|columns=1fr 1fr|gap=5px|class_name=card|
<|c1|
**Gabarito**
|>
<|c2|
**Submetidos**
|>
<|c3|
<|{gabarito}|file_selector|class_name=fullwidth|label=Coloque seu arquivo de gabarito aqui|extensions=.py|>
<|{dados}|file_selector|class_name=fullwidth|label=Coloque seu arquivo de dados do gabarito aqui|extensions=.csv,.json|>
|>
<|c4|
<|{questoes}|file_selector|class_name=fullwidth|label=Suba o arquivo zip com as respostas aqui|extensions=.zip|>
|>
|>
---
<br/>
<center><|Corrigir|button|on_action=evaluate|><|{download_content}|file_download|label=Download|name={download_file}|active={download_ativo}|on_action=download_start|></center>
<br/>
<br/>
<|{resultado}|input|multiline|label=Resultado|class_name=fullwidth|>
|>
"""
)
