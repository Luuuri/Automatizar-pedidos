# ─────────────────────────────────────────────
#  main.py — ponto de entrada
#  Execute:  python main.py
# ─────────────────────────────────────────────

import sys
import os

# Adiciona o diretório atual ao path para o executável
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pages.interface import App

if __name__ == "__main__":
    app = App()
    app.mainloop()