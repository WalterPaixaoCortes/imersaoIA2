"""OpenAI API connector."""

# Import from standard library
import logging

# Import from 3rd party libraries
from openai import OpenAI

import utils.config as config

# Suppress openai request/response logging
# Handle by manually changing the respective APIRequestor methods in the openai package
# Does not work hosted on Streamlit since all packages are re-installed by Poetry
# Alternatively (affects all messages from this logger):
logging.getLogger("openai").setLevel(logging.WARNING)


class Openai:
    """OpenAI Connector."""

    client = None

    def __init__(self):
        self.client = None

    def build_prompt(
        self,
        nivel: str,
        objetivo: str,
        tipo: str,
        area: str,
        tem_introducao: str,
        tem_resposta: str,
        gera_alternativas: str,
    ):
        if tipo in [
            "Escolha Simples",
            "Escolha Múltipla",
            "Dissertativa",
            "Completar as Lacunas",
        ]:
            base_prompt = config.PROMPTS[tipo].format(
                nivel, objetivo, tipo, area, tem_introducao, tem_resposta
            )
        elif tipo in [
            "Lógica - O que Faz",
            "Lógica - Qual o Resultado",
            "Lógica - Qual o Erro",
            "Lógica - Qual comando",
        ]:
            base_prompt = config.PROMPTS2[tipo].format(
                nivel,
                objetivo,
                tipo,
                area,
                tem_introducao,
                tem_resposta,
                gera_alternativas,
            )
        else:
            base_prompt = f"""Você é um especialista em Ciência de Dados.
        Elabore uma questão de nível {nivel} sobre a ementa descrita abaixo:
        Ementa: {objetivo}
        A questão deve ser do tipo: {tipo}
        A questão aborda a área: {area}
        A questão deve ser estruturada da seguinte forma:"""

            if tem_introducao == "Sim":
                base_prompt = (
                    base_prompt + """\n- Apresenta-se uma introdução ao conteúdo"""
                )

            if tipo == "Código SQL":
                base_prompt = (
                    base_prompt
                    + """\n- Apresenta-se o enunciado da questão seguindo o formato:
            - Gera-se uma tabela de dados ficticios
            - Imprime-se a tabela de dados
            - Faz-se uma pergunta que o aluno deve responder com uma instrução SQL"""
                )
            elif tipo == "Código Python":
                base_prompt = (
                    base_prompt
                    + """\n- Apresenta-se o enunciado da questão seguindo o formato:
            - Gera-se uma tabela de dados ficticios
            - Mostra-se a tabela de dados
            - Faz-se uma pergunta que o aluno deve responder com um script Python que pode utilizar as bibliotecas pandas, matplotlib, requests e todas as biliotecas nativas do python"""
                )
            else:
                base_prompt = (
                    base_prompt + """\n- Apresenta-se o enunciado da questão"""
                )

            if tem_resposta == "Sim":
                base_prompt = (
                    base_prompt
                    + """\n- Apresenta-se a resposta correta, e explique a resposta."""
                )

            if tipo == "Código Python":
                base_prompt = (
                    base_prompt
                    + """\n- Gere dois testes unitários para validar o código, que deverá utilizar um arquivo de entrada."""
                )

        competencias = "\n".join(
            [
                f'{comp["titulo"]} - {comp["descricao"]}'
                for comp in config.bncc_competencias
            ]
        )
        bncc = f"""\n- Relacione a questão gerada com até duas competências da BNCC que estão listadas abaixo: 
                    - Apresente as duas competências selecionadas com o seguinte formato
                    Compentencia <numero>. <titulo competência> - <descricao competência> - <explicacao sobre como a questão se relaciona com a competência>
                    {competencias}"""

        objetivos = """\n Gere dois objetivos de ensino, seguindo a taxonomia de Bloom, para a questão."""
        return base_prompt + bncc + objetivos

    def set_key(self, key: str):
        self.client = OpenAI(api_key=key)

    def moderate(self, prompt: str) -> bool:
        """Call OpenAI GPT Moderation with text prompt.
        Args:
            prompt: text prompt
        Return: boolean if flagged
        """
        try:
            response = openai.Moderation.create(prompt)
            return response["results"][0]["flagged"]
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")

    def complete(
        self, prompt: str, temperature: float = 0.9, max_tokens: int = 2048
    ) -> str:
        """Call OpenAI GPT Completion with text prompt.
        Args:
            prompt: text prompt
        Return: predicted response text
        """
        kwargs = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1,  # default
            "frequency_penalty": 0,  # default,
            "presence_penalty": 0,  # default
        }
        try:
            response = self.client.chat.completions.create(**kwargs)

            lst_resp = [x.message.content for x in response.choices]
            return "\n".join(lst_resp)

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")

    def image(self, prompt: str) -> str:
        """Call OpenAI Image Create with text prompt.
        Args:
            prompt: text prompt
        Return: image url
        """
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512",
                response_format="url",
            )
            return response["data"][0]["url"]

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
