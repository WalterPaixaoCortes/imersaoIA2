# -*- coding: utf-8 -*-
import os

from taipy.gui import Gui
from dotenv import load_dotenv

load_dotenv()

from pages.generate import gen_q_md
from pages.visualize import tbl_q_md
from pages.report import sum_q_md

pages = {
    "/": "<center><|navbar|></center>",
    "Gerar": gen_q_md,
    "Visualizar": tbl_q_md,
    "Sumario": sum_q_md,
}


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
if __name__ == "__main__":
    Gui(pages=pages).run(
        title="EduAssist.ai - Gerador de Questões",
        host="0.0.0.0",
        port=os.getenv("PORT"),
        use_reloader=True,
    )
