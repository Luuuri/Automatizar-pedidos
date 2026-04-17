# ─────────────────────────────────────────────
#  pages/interface.py — interface gráfica Tkinter
# ─────────────────────────────────────────────

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import date
import os
import json

from config import TODOS_CLIENTES, PAGAMENTOS, ESPECIES

# ── Caminhos ──────────────────────────────────
_BASE       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH    = os.path.join(_BASE, "data", "log.txt")
CONFIG_PATH = os.path.join(_BASE, "data", "config.json")
FILA_PATH   = os.path.join(_BASE, "data", "fila.json")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def _carregar_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _salvar_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _salvar_log(texto):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    except Exception:
        pass

def _carregar_log():
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ── Paleta SGEP ───────────────────────────────
COR = {
    "janela":      "#f0f2f5",
    "fundo":       "#ffffff",
    "borda":       "#d0d7de",
    "borda_focus": "#2c7be5",
    "acento":      "#2c5f8a",
    "acento_btn":  "#3a7abf",
    "acento_hov":  "#2c6aa0",
    "texto":       "#1a2535",
    "texto_fraco": "#6b7a8d",
    "texto_branco":"#ffffff",
    "verde":       "#1a7f4e",
    "amarelo":     "#856404",
    "aba_inativa": "#dce3ec",
    "aba_ativa":   "#ffffff",
    "cabecalho":   "#1e3a5f",
    "rodape":      "#e8ecf0",
}

FONTE_LABEL  = ("Segoe UI", 9)
FONTE_INPUT  = ("Segoe UI", 10)
FONTE_BTN    = ("Segoe UI", 9, "bold")
FONTE_LOG    = ("Consolas", 8)
FONTE_CABEC  = ("Segoe UI", 13, "bold")

# ── Estilos ───────────────────────────────────
def _aplicar_estilos():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("SGEP.TNotebook",
        background=COR["janela"], borderwidth=0, tabmargins=[0,0,0,0])
    s.configure("SGEP.TNotebook.Tab",
        background=COR["aba_inativa"], foreground=COR["texto_fraco"],
        font=("Segoe UI", 9, "bold"), padding=[14, 6], borderwidth=1, relief="flat")
    s.map("SGEP.TNotebook.Tab",
        background=[("selected", COR["aba_ativa"])],
        foreground=[("selected", COR["acento_btn"])])
    s.configure("SGEP.TCombobox",
        fieldbackground=COR["fundo"], background=COR["fundo"],
        foreground=COR["texto"], selectbackground=COR["acento_btn"],
        selectforeground=COR["texto_branco"], arrowcolor=COR["acento_btn"],
        bordercolor=COR["borda"], lightcolor=COR["borda"], darkcolor=COR["borda"])
    s.map("SGEP.TCombobox",
        fieldbackground=[("readonly", COR["fundo"])],
        foreground=[("readonly", COR["texto"])],
        bordercolor=[("focus", COR["borda_focus"])])
    s.configure("SGEP.Treeview",
        background=COR["fundo"], foreground=COR["texto"],
        fieldbackground=COR["fundo"], borderwidth=1,
        font=FONTE_INPUT, rowheight=26, relief="solid")
    s.configure("SGEP.Treeview.Heading",
        background=COR["acento_btn"], foreground=COR["texto_branco"],
        font=("Segoe UI", 9, "bold"), borderwidth=0, relief="flat", padding=4)
    s.map("SGEP.Treeview",
        background=[("selected", COR["acento_btn"])],
        foreground=[("selected", COR["texto_branco"])])
    s.configure("SGEP.Vertical.TScrollbar",
        background=COR["borda"], troughcolor=COR["janela"],
        arrowcolor=COR["texto_fraco"], borderwidth=0)

# ── Widgets ───────────────────────────────────
def _entry(parent, var=None, width=24, readonly=False):
    e = tk.Entry(parent, textvariable=var, font=FONTE_INPUT,
                 bg=COR["janela"] if readonly else COR["fundo"],
                 fg=COR["texto_fraco"] if readonly else COR["texto"],
                 relief="solid", bd=1, width=width,
                 highlightthickness=1,
                 highlightbackground=COR["borda"],
                 highlightcolor=COR["borda_focus"],
                 state="disabled" if readonly else "normal",
                 disabledforeground=COR["texto_fraco"],
                 disabledbackground=COR["janela"])
    return e

def _combo(parent, values, var=None, width=22):
    return ttk.Combobox(parent, values=values, textvariable=var,
                        font=FONTE_INPUT, style="SGEP.TCombobox",
                        width=width, state="normal")

def _label(parent, texto, fraco=False, bg=None):
    return tk.Label(parent, text=texto, font=FONTE_LABEL,
                    bg=bg or COR["fundo"],
                    fg=COR["texto_fraco"] if fraco else COR["texto"])

def _btn_primario(parent, texto, cmd, **kw):
    return tk.Button(parent, text=texto, command=cmd, font=FONTE_BTN,
                     bg=COR["acento_btn"], fg=COR["texto_branco"],
                     activebackground=COR["acento_hov"],
                     activeforeground=COR["texto_branco"],
                     relief="flat", cursor="hand2", padx=14, pady=5, **kw)

def _btn_secundario(parent, texto, cmd, **kw):
    return tk.Button(parent, text=texto, command=cmd, font=FONTE_BTN,
                     bg=COR["borda"], fg=COR["texto"],
                     activebackground="#bec8d4",
                     activeforeground=COR["texto"],
                     relief="flat", cursor="hand2", padx=14, pady=5, **kw)

def _card(parent, titulo=None):
    outer = tk.Frame(parent, bg=COR["borda"])
    inner = tk.Frame(outer, bg=COR["fundo"])
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    if titulo:
        cab = tk.Frame(inner, bg=COR["acento_btn"], height=26)
        cab.pack(fill="x")
        tk.Label(cab, text=f"  {titulo}", font=("Segoe UI", 9, "bold"),
                 bg=COR["acento_btn"], fg=COR["texto_branco"]).pack(side="left", pady=3)
        corpo = tk.Frame(inner, bg=COR["fundo"])
        corpo.pack(fill="both", expand=True)
        return outer, corpo
    return outer, inner

def _filtrar(combo, lista, digitado):
    f = [x for x in lista if digitado.lower() in x.lower()]
    combo["values"] = f if f else lista

# ── App ───────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SGEP — Automação de Pedidos")
        self.configure(bg=COR["janela"])
        self.resizable(True, True)
        self.minsize(860, 700)
        self.geometry("960x760")

        # fila: lista de dicts {dados, itens, baixar_pdf, codigo, status}
        self.fila = []
        # itens do pedido sendo montado agora
        self.itens = []

        _aplicar_estilos()
        self._build()
        self._carregar_log_salvo()
        self._centralizar()

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Layout ───────────────────────────────

    def _build(self):
        cab = tk.Frame(self, bg=COR["cabecalho"], height=48)
        cab.pack(fill="x")
        cab.pack_propagate(False)
        tk.Label(cab, text="🐟  SGEP — Automação de Pedidos",
                 font=FONTE_CABEC, bg=COR["cabecalho"],
                 fg=COR["texto_branco"]).pack(side="left", padx=16, pady=10)
        tk.Label(cab, text="Americo Lima  |  AMASA Belém",
                 font=FONTE_LABEL, bg=COR["cabecalho"],
                 fg="#8daac8").pack(side="right", padx=16)

        self.nb = ttk.Notebook(self, style="SGEP.TNotebook")
        self.nb.pack(fill="both", expand=True)

        self._aba_pedido()
        self._aba_itens()
        self._aba_fila()
        self._aba_conferir()
        self._aba_planilhas()
        self._aba_log()

        rod = tk.Frame(self, bg=COR["rodape"], height=28)
        rod.pack(fill="x", side="bottom")
        rod.pack_propagate(False)
        self._status_var = tk.StringVar(value="Pronto.")
        tk.Label(rod, textvariable=self._status_var,
                 font=("Segoe UI", 8), bg=COR["rodape"],
                 fg=COR["texto_fraco"]).pack(side="left", padx=10, pady=4)

    def _status(self, msg):
        self._status_var.set(msg)

    # ── Aba 1 — Pedido ───────────────────────

    def _aba_pedido(self):
        frame = tk.Frame(self.nb, bg=COR["janela"])
        self.nb.add(frame, text="  Pedido  ")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        outer, corpo = _card(frame, titulo="Informações do Pedido")
        outer.grid(row=0, column=0, columnspan=2,
                   sticky="ew", padx=12, pady=(10, 6))
        corpo.columnconfigure(1, weight=1)
        corpo.columnconfigure(3, weight=1)

        self.v_ordem = tk.StringVar(value="0")
        _label(corpo, "Ordem Compra", fraco=True).grid(
            row=0, column=0, sticky="w", padx=(12,6), pady=(10,2))
        _entry(corpo, self.v_ordem, width=14).grid(
            row=0, column=1, sticky="w", padx=(0,20), pady=(10,2))

        self.v_data = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        _label(corpo, "Prev. Entrega", fraco=True).grid(
            row=0, column=2, sticky="w", padx=(0,6), pady=(10,2))
        _entry(corpo, self.v_data, width=14).grid(
            row=0, column=3, sticky="w", padx=(0,12), pady=(10,2))

        self.v_empresa = tk.StringVar(
            value="AMAZONAS INDUSTRIAS ALIMENTICIAS S A AMASA — BELÉM")
        _label(corpo, "Empresa", fraco=True).grid(
            row=1, column=0, sticky="w", padx=(12,6), pady=(6,2))
        _entry(corpo, self.v_empresa, width=52, readonly=True).grid(
            row=1, column=1, columnspan=3, sticky="ew", padx=(0,12), pady=(6,2))

        self.v_cliente = tk.StringVar()
        _label(corpo, "Cliente", fraco=True).grid(
            row=2, column=0, sticky="w", padx=(12,6), pady=(6,2))
        cb_cli = _combo(corpo, TODOS_CLIENTES, self.v_cliente, width=40)
        cb_cli.bind("<KeyRelease>",
                    lambda e: _filtrar(cb_cli, TODOS_CLIENTES, self.v_cliente.get()))
        cb_cli.grid(row=2, column=1, columnspan=3, sticky="ew", padx=(0,12), pady=(6,2))

        self.v_vendedor = tk.StringVar(value="Americo Lima  (único disponível)")
        _label(corpo, "Vendedor", fraco=True).grid(
            row=3, column=0, sticky="w", padx=(12,6), pady=(6,2))
        _entry(corpo, self.v_vendedor, width=28, readonly=True).grid(
            row=3, column=1, sticky="ew", padx=(0,20), pady=(6,2))

        self.v_pagto = tk.StringVar()
        _label(corpo, "Cond. Pagto", fraco=True).grid(
            row=3, column=2, sticky="w", padx=(0,6), pady=(6,2))
        cb_pag = _combo(corpo, PAGAMENTOS, self.v_pagto, width=18)
        cb_pag.bind("<KeyRelease>",
                    lambda e: _filtrar(cb_pag, PAGAMENTOS, self.v_pagto.get()))
        cb_pag.grid(row=3, column=3, sticky="ew", padx=(0,12), pady=(6,2))

        _label(corpo, "Observações", fraco=True).grid(
            row=4, column=0, sticky="nw", padx=(12,6), pady=(6,2))
        self.txt_obs = tk.Text(
            corpo, font=FONTE_INPUT, bg=COR["fundo"], fg=COR["texto"],
            insertbackground=COR["acento_btn"],
            relief="solid", bd=1, width=52, height=3, wrap="word")
        self.txt_obs.grid(row=4, column=1, columnspan=3, sticky="ew",
                          padx=(0,12), pady=(6,8))

        # Opções
        outer_op, corpo_op = _card(frame, titulo="Opções")
        outer_op.grid(row=1, column=0, sticky="nsew", padx=(12,6), pady=(0,10))

        self.v_baixar_pdf = tk.BooleanVar(value=False)
        tk.Checkbutton(corpo_op, text="Baixar PDF após criar",
                       variable=self.v_baixar_pdf,
                       font=FONTE_INPUT, bg=COR["fundo"], fg=COR["texto"],
                       activebackground=COR["fundo"], selectcolor=COR["fundo"],
                       cursor="hand2").pack(anchor="w", padx=12, pady=(10,4))
        _label(corpo_op, "PDF salvo automaticamente em D:\\Documento\\#Pedidos",
               fraco=True).pack(anchor="w", padx=12, pady=(0,10))

        # Botões
        outer_btn, corpo_btn = _card(frame, titulo="")
        outer_btn.grid(row=1, column=1, sticky="nsew", padx=(6,12), pady=(0,10))

        _btn_primario(corpo_btn, "  Ir para Itens  →",
                      lambda: self.nb.select(1)).pack(pady=(16,8), padx=16, fill="x")
        _btn_secundario(corpo_btn, "  Limpar Formulário",
                        self._limpar_pedido).pack(pady=(0,8), padx=16, fill="x")

    # ── Aba 2 — Itens ────────────────────────

    def _aba_itens(self):
        frame = tk.Frame(self.nb, bg=COR["janela"])
        self.nb.add(frame, text="  Itens Pedidos  ")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        outer, corpo = _card(frame, titulo="Novo Item")
        outer.grid(row=0, column=0, sticky="ew", padx=12, pady=(10,6))
        corpo.columnconfigure(1, weight=1)
        corpo.columnconfigure(3, weight=1)
        corpo.columnconfigure(5, weight=1)

        self.v_esp = tk.StringVar()
        _label(corpo, "Espécie", fraco=True).grid(
            row=0, column=0, sticky="w", padx=(12,6), pady=(10,2))
        cb_esp = _combo(corpo, ESPECIES, self.v_esp, width=14)
        cb_esp.bind("<KeyRelease>",
                    lambda e: _filtrar(cb_esp, ESPECIES, self.v_esp.get()))
        cb_esp.grid(row=0, column=1, sticky="ew", padx=(0,16), pady=(10,2))

        self.v_pa = tk.StringVar()
        _label(corpo, "PA", fraco=True).grid(
            row=0, column=2, sticky="w", padx=(0,6), pady=(10,2))
        _entry(corpo, self.v_pa, width=8).grid(
            row=0, column=3, sticky="w", padx=(0,16), pady=(10,2))

        self.v_qtd = tk.StringVar()
        _label(corpo, "Qtd (kg)", fraco=True).grid(
            row=0, column=4, sticky="w", padx=(0,6), pady=(10,2))
        _entry(corpo, self.v_qtd, width=10).grid(
            row=0, column=5, sticky="ew", padx=(0,16), pady=(10,2))

        self.v_val = tk.StringVar()
        _label(corpo, "Valor Unit.", fraco=True).grid(
            row=0, column=6, sticky="w", padx=(0,6), pady=(10,2))
        _entry(corpo, self.v_val, width=10).grid(
            row=0, column=7, sticky="ew", padx=(0,12), pady=(10,2))

        _label(corpo, "Uni. Medida sempre KG — valor comparado com o sistema automaticamente",
               fraco=True).grid(
            row=1, column=0, columnspan=6, sticky="w", padx=(12,0), pady=(0,6))
        _btn_primario(corpo, "+ Adicionar", self._add_item).grid(
            row=1, column=6, columnspan=2, padx=(0,12), pady=(0,8), sticky="e")

        outer_t, corpo_t = _card(frame, titulo="Itens do Pedido Atual")
        outer_t.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,6))
        corpo_t.columnconfigure(0, weight=1)
        corpo_t.rowconfigure(0, weight=1)

        cols = ("Espécie", "PA", "Qtd (kg)", "Valor Solicitado")
        self.tree = ttk.Treeview(corpo_t, columns=cols, show="headings",
                                  style="SGEP.Treeview", height=7)
        for col, w in zip(cols, (180, 80, 100, 120)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(corpo_t, orient="vertical",
                           command=self.tree.yview,
                           style="SGEP.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=6)
        sb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0,4))

        btn_row = tk.Frame(frame, bg=COR["janela"])
        btn_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(0,10))

        _btn_secundario(btn_row, "✕  Remover Item", self._remover).pack(side="left")
        _btn_secundario(btn_row, "← Voltar ao Pedido",
                        lambda: self.nb.select(0)).pack(side="left", padx=(8,0))
        _btn_primario(btn_row, "＋  Adicionar à Fila",
                      self._adicionar_fila).pack(side="right")

    # ── Aba 3 — Fila ─────────────────────────

    def _aba_fila(self):
        frame = tk.Frame(self.nb, bg=COR["janela"])
        self.nb.add(frame, text="  Fila  ")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        outer_t, corpo_t = _card(frame, titulo="Pedidos na Fila")
        outer_t.grid(row=0, column=0, sticky="nsew", padx=12, pady=(10,6))
        corpo_t.columnconfigure(0, weight=1)
        corpo_t.rowconfigure(0, weight=1)

        cols = ("#", "Cliente", "Data", "Itens", "PDF", "Status")
        self.tree_fila = ttk.Treeview(corpo_t, columns=cols, show="headings",
                                       style="SGEP.Treeview", height=12)
        for col, w in zip(cols, (40, 220, 90, 50, 40, 110)):
            self.tree_fila.heading(col, text=col)
            self.tree_fila.column(col, width=w, anchor="center")
        self.tree_fila.column("Cliente", anchor="w")

        sb = ttk.Scrollbar(corpo_t, orient="vertical",
                           command=self.tree_fila.yview,
                           style="SGEP.Vertical.TScrollbar")
        self.tree_fila.configure(yscrollcommand=sb.set)
        self.tree_fila.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=6)
        sb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0,4))

        # tags de cor por status
        self.tree_fila.tag_configure("pendente",  background="#fff9e6")
        self.tree_fila.tag_configure("concluido", background="#e8f5e9")
        self.tree_fila.tag_configure("erro",      background="#fdecea")
        self.tree_fila.tag_configure("rodando",   background="#e3f2fd")

        btn_row = tk.Frame(frame, bg=COR["janela"])
        btn_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,10))

        _btn_secundario(btn_row, "✕  Remover da Fila",
                        self._remover_da_fila).pack(side="left")
        _btn_secundario(btn_row, "↑  Mover para Cima",
                        lambda: self._mover_fila(-1)).pack(side="left", padx=(8,0))
        _btn_secundario(btn_row, "↓  Mover para Baixo",
                        lambda: self._mover_fila(1)).pack(side="left", padx=(8,0))
        _btn_primario(btn_row, "▶  Executar Fila Completa",
                      self._executar_fila).pack(side="right")

    # ── Aba 4 — Conferir ─────────────────────

    def _aba_conferir(self):
        frame = tk.Frame(self.nb, bg=COR["janela"])
        self.nb.add(frame, text="  Conferir  ")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        outer_t, corpo_t = _card(frame,
            titulo="Pedidos Concluídos — Clique para marcar e conferir no sistema")
        outer_t.grid(row=0, column=0, sticky="nsew", padx=12, pady=(10,6))
        corpo_t.columnconfigure(0, weight=1)
        corpo_t.rowconfigure(0, weight=1)

        cols = ("Código", "Cliente", "Data", "PDF")
        self.tree_conf = ttk.Treeview(corpo_t, columns=cols, show="headings",
                                       style="SGEP.Treeview", height=12,
                                       selectmode="extended")
        for col, w in zip(cols, (80, 280, 100, 60)):
            self.tree_conf.heading(col, text=col)
            self.tree_conf.column(col, width=w, anchor="center")
        self.tree_conf.column("Cliente", anchor="w")

        sb = ttk.Scrollbar(corpo_t, orient="vertical",
                           command=self.tree_conf.yview,
                           style="SGEP.Vertical.TScrollbar")
        self.tree_conf.configure(yscrollcommand=sb.set)
        self.tree_conf.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=6)
        sb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0,4))

        _label(corpo_t,
               "Selecione um ou mais pedidos (Ctrl+clique) e clique em Conferir.",
               fraco=True).grid(row=1, column=0, columnspan=2,
                                sticky="w", padx=8, pady=(0,4))

        btn_row = tk.Frame(frame, bg=COR["janela"])
        btn_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,10))

        _btn_secundario(btn_row, "✕  Remover da Lista",
                        self._remover_da_conferencia).pack(side="left")
        _btn_primario(btn_row, "✔  Conferir Selecionados no Sistema",
                      self._conferir_selecionados).pack(side="right")

    # ── Aba 5 — Planilhas ────────────────────

    def _aba_planilhas(self):
        frame = tk.Frame(self.nb, bg=COR["janela"])
        self.nb.add(frame, text="  Planilhas  ")
        frame.columnconfigure(0, weight=1)

        cfg = _carregar_config()

        outer_c, corpo_c = _card(frame, titulo="Arquivos Excel")
        outer_c.grid(row=0, column=0, sticky="ew", padx=12, pady=(10,6))
        corpo_c.columnconfigure(1, weight=1)

        _label(corpo_c, "Relatório Mensal", fraco=True).grid(
            row=0, column=0, sticky="w", padx=(12,8), pady=(10,4))
        self.v_rel = tk.StringVar(value=cfg.get("relatorio", ""))
        _entry(corpo_c, self.v_rel, width=46).grid(
            row=0, column=1, sticky="ew", padx=(0,4), pady=(10,4))
        tk.Button(corpo_c, text="...", font=FONTE_LABEL,
                  bg=COR["borda"], fg=COR["texto"], relief="flat",
                  cursor="hand2", padx=6,
                  command=lambda: self._escolher_arquivo(
                      self.v_rel, "Selecione o Relatório Mensal")).grid(
            row=0, column=2, padx=(0,12), pady=(10,4))

        _label(corpo_c, "Programação de Vendas", fraco=True).grid(
            row=1, column=0, sticky="w", padx=(12,8), pady=(4,4))
        self.v_prog = tk.StringVar(value=cfg.get("programacao", ""))
        _entry(corpo_c, self.v_prog, width=46).grid(
            row=1, column=1, sticky="ew", padx=(0,4), pady=(4,4))
        tk.Button(corpo_c, text="...", font=FONTE_LABEL,
                  bg=COR["borda"], fg=COR["texto"], relief="flat",
                  cursor="hand2", padx=6,
                  command=lambda: self._escolher_arquivo(
                      self.v_prog, "Selecione a Programação de Vendas")).grid(
            row=1, column=2, padx=(0,12), pady=(4,4))

        _btn_primario(corpo_c, "Salvar caminhos",
                      self._salvar_caminhos_planilhas).grid(
            row=2, column=0, columnspan=3, pady=(4,12), padx=12, sticky="e")

        outer_f, corpo_f = _card(frame, titulo="Preencher via Foto do Impresso")
        outer_f.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,6))
        corpo_f.columnconfigure(0, weight=1)

        _label(corpo_f,
               "Fotografe o impresso do seu pai e selecione a imagem. "
               "A IA lê os dados e preenche as duas planilhas automaticamente.",
               fraco=True).pack(anchor="w", padx=12, pady=(10,6))

        pf = tk.Frame(corpo_f, bg=COR["fundo"])
        pf.pack(fill="x", padx=12, pady=(0,8))
        _label(pf, "Período da semana:").pack(side="left")
        self.v_periodo = tk.StringVar(value="C")
        for letra, rotulo in [("C","01–10"),("D","13–17"),("E","20–24"),("F","27–30")]:
            tk.Radiobutton(pf, text=rotulo, value=letra, variable=self.v_periodo,
                           font=FONTE_LABEL, bg=COR["fundo"], fg=COR["texto"],
                           selectcolor=COR["fundo"], activebackground=COR["fundo"],
                           cursor="hand2").pack(side="left", padx=(8,0))

        _btn_primario(corpo_f, "📷  Selecionar Foto e Preencher",
                      self._preencher_via_foto).pack(pady=(0,12), padx=12, fill="x")

        outer_r, corpo_r = _card(frame, titulo="Resultado")
        outer_r.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0,10))
        frame.rowconfigure(2, weight=1)
        corpo_r.columnconfigure(0, weight=1)
        corpo_r.rowconfigure(0, weight=1)

        self.txt_planilha_resultado = tk.Text(
            corpo_r, font=FONTE_LOG, bg="#1a1e2e", fg="#c8d3e0",
            relief="flat", state="disabled", wrap="word", height=7)
        sb2 = ttk.Scrollbar(corpo_r, orient="vertical",
                            command=self.txt_planilha_resultado.yview,
                            style="SGEP.Vertical.TScrollbar")
        self.txt_planilha_resultado.configure(yscrollcommand=sb2.set)
        self.txt_planilha_resultado.grid(row=0, column=0, sticky="nsew",
                                          padx=(6,0), pady=6)
        sb2.grid(row=0, column=1, sticky="ns", pady=6, padx=(0,4))
        for tag, cor in [("ok","#4ade80"),("erro","#f87171"),
                         ("aviso","#fbbf24"),("info","#60a5fa")]:
            self.txt_planilha_resultado.tag_config(tag, foreground=cor)

    # ── Aba 6 — Log ──────────────────────────

    def _aba_log(self):
        frame = tk.Frame(self.nb, bg=COR["janela"])
        self.nb.add(frame, text="  Log  ")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        outer, corpo = _card(frame, titulo="Histórico de Execuções")
        outer.grid(row=0, column=0, sticky="nsew", padx=12, pady=(10,6))
        corpo.columnconfigure(0, weight=1)
        corpo.rowconfigure(0, weight=1)

        self.log_txt = tk.Text(
            corpo, font=FONTE_LOG, bg="#1a1e2e", fg="#c8d3e0",
            insertbackground=COR["acento_btn"],
            relief="flat", state="disabled", wrap="word")
        sb = ttk.Scrollbar(corpo, orient="vertical",
                           command=self.log_txt.yview,
                           style="SGEP.Vertical.TScrollbar")
        self.log_txt.configure(yscrollcommand=sb.set)
        self.log_txt.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=6)
        sb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0,4))
        for tag, cor in [("ok","#4ade80"),("erro","#f87171"),
                         ("aviso","#fbbf24"),("info","#60a5fa"),("normal","#c8d3e0")]:
            self.log_txt.tag_config(tag, foreground=cor)

        btn_row = tk.Frame(frame, bg=COR["janela"])
        btn_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,10))
        _btn_secundario(btn_row, "Limpar Log", self._limpar_log).pack(side="right")

    # ── Helpers de log ────────────────────────

    def log(self, msg, tipo="normal"):
        self.log_txt.configure(state="normal")
        self.log_txt.insert("end", msg + "\n", tipo)
        self.log_txt.see("end")
        self.log_txt.configure(state="disabled")
        _salvar_log(msg)

    def _carregar_log_salvo(self):
        conteudo = _carregar_log()
        if conteudo:
            self.log_txt.configure(state="normal")
            self.log_txt.insert("1.0", conteudo)
            self.log_txt.see("end")
            self.log_txt.configure(state="disabled")

    def _limpar_log(self):
        if messagebox.askyesno("Limpar Log", "Apagar todo o histórico?"):
            self.log_txt.configure(state="normal")
            self.log_txt.delete("1.0", "end")
            self.log_txt.configure(state="disabled")
            try:
                open(LOG_PATH, "w").close()
            except Exception:
                pass

    # ── Helpers do formulário ─────────────────

    def _limpar_pedido(self):
        self.v_ordem.set("0")
        self.v_data.set(date.today().strftime("%d/%m/%Y"))
        self.v_cliente.set("")
        self.v_pagto.set("")
        self.txt_obs.delete("1.0", "end")

    def _limpar_itens_form(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.itens.clear()
        self.v_esp.set(""); self.v_pa.set("")
        self.v_qtd.set(""); self.v_val.set("")

    def _add_item(self):
        esp = self.v_esp.get().strip().lower()
        pa  = self.v_pa.get().strip().zfill(4)
        qtd = self.v_qtd.get().strip().replace(",", ".")
        val = self.v_val.get().strip().replace(",", ".")

        if not esp:
            messagebox.showwarning("Campo vazio", "Preencha a Espécie."); return
        if pa == "0000":
            messagebox.showwarning("Campo vazio", "Preencha o PA."); return
        try:
            qtd_f = float(qtd)
        except ValueError:
            messagebox.showerror("Inválido", "Quantidade deve ser número."); return
        try:
            val_f = float(val)
        except ValueError:
            messagebox.showerror("Inválido", "Valor deve ser número."); return

        self.itens.append({"especie": esp, "pa": pa, "quantidade": qtd_f, "valor": val_f})
        self.tree.insert("", "end", values=(
            esp.capitalize(), pa,
            f"{qtd_f:.3f}".rstrip("0").rstrip("."),
            f"R$ {val_f:.2f}"))
        self.v_esp.set(""); self.v_pa.set("")
        self.v_qtd.set(""); self.v_val.set("")

    def _remover(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        self.tree.delete(sel[0])
        self.itens.pop(idx)

    def _validar_pedido(self):
        erros = []
        if not self.v_ordem.get().strip():  erros.append("Ordem de Compra")
        if not self.v_data.get().strip():   erros.append("Data de Entrega")
        if not self.v_cliente.get().strip():erros.append("Cliente")
        if not self.v_pagto.get().strip():  erros.append("Cond. Pagamento")
        if not self.itens: erros.append("Nenhum item adicionado")
        return erros

    # ── Fila ─────────────────────────────────

    def _adicionar_fila(self):
        erros = self._validar_pedido()
        if erros:
            messagebox.showerror("Campos obrigatórios",
                "Preencha antes de adicionar à fila:\n\n• " + "\n• ".join(erros))
            return

        entrada = {
            "dados": {
                "ordem":          self.v_ordem.get().strip(),
                "data":           self.v_data.get().strip(),
                "cliente":        self.v_cliente.get().strip().lower(),
                "pagamento":      self.v_pagto.get().strip().lower(),
                "observacao":     self.txt_obs.get("1.0", "end").strip(),
                "empresa_index":  1,
                "vendedor_index": 1,
            },
            "itens":      list(self.itens),
            "baixar_pdf": self.v_baixar_pdf.get(),
            "codigo":     None,
            "status":     "pendente",
        }
        self.fila.append(entrada)

        n = len(self.fila)
        self.tree_fila.insert("", "end",
            iid=str(n - 1),
            values=(n,
                    self.v_cliente.get().strip(),
                    self.v_data.get().strip(),
                    len(self.itens),
                    "Sim" if self.v_baixar_pdf.get() else "Não",
                    "⏳ Pendente"),
            tags=("pendente",))

        messagebox.showinfo("Adicionado à Fila",
            f"Pedido de {self.v_cliente.get()} adicionado!\n"
            f"Total na fila: {n} pedido(s).\n\n"
            "Preencha o próximo pedido ou vá para a aba Fila para executar.")

        # Limpa formulário para o próximo pedido
        self._limpar_pedido()
        self._limpar_itens_form()
        self.nb.select(0)

    def _remover_da_fila(self):
        sel = self.tree_fila.selection()
        if not sel: return
        idx = int(sel[0])
        if self.fila[idx]["status"] == "rodando":
            messagebox.showwarning("Em execução",
                "Não é possível remover um pedido que está sendo executado.")
            return
        self.tree_fila.delete(sel[0])
        self.fila.pop(idx)
        # Renumera
        self._atualizar_tree_fila()

    def _mover_fila(self, direcao):
        sel = self.tree_fila.selection()
        if not sel: return
        idx = int(sel[0])
        novo = idx + direcao
        if novo < 0 or novo >= len(self.fila): return
        self.fila[idx], self.fila[novo] = self.fila[novo], self.fila[idx]
        self._atualizar_tree_fila()

    def _atualizar_tree_fila(self):
        for item in self.tree_fila.get_children():
            self.tree_fila.delete(item)
        for i, p in enumerate(self.fila):
            status_txt = {
                "pendente":  "⏳ Pendente",
                "rodando":   "🔄 Executando",
                "concluido": "✔ Concluído",
                "erro":      "✗ Erro",
            }.get(p["status"], p["status"])
            self.tree_fila.insert("", "end", iid=str(i),
                values=(i+1,
                        p["dados"]["cliente"],
                        p["dados"]["data"],
                        len(p["itens"]),
                        "Sim" if p["baixar_pdf"] else "Não",
                        status_txt),
                tags=(p["status"],))

    def _executar_fila(self):
        pendentes = [p for p in self.fila if p["status"] == "pendente"]
        if not pendentes:
            messagebox.showinfo("Fila vazia",
                "Nenhum pedido pendente na fila.\nAdicione pedidos antes de executar.")
            return

        if not messagebox.askyesno("Confirmar",
            f"{len(pendentes)} pedido(s) serão executados em sequência.\n\nContinuar?"):
            return

        self.nb.select(5)  # aba Log
        self.log("═" * 55, "info")
        self.log(f"  INICIANDO FILA — {len(pendentes)} pedido(s)"
                 f"  {date.today().strftime('%d/%m/%Y %H:%M')}", "info")
        self.log("═" * 55, "info")
        self._status("Executando fila...")

        threading.Thread(target=self._rodar_fila, daemon=True).start()

    def _rodar_fila(self):
        import builtins
        _orig = builtins.print

        def _gui_print(*args, **kw):
            msg = " ".join(str(a) for a in args)
            tipo = ("ok"    if "[OK]"    in msg else
                    "erro"  if "[ERRO]"  in msg or "[PULADO]" in msg else
                    "aviso" if "[AVISO]" in msg or "INFERIOR" in msg else
                    "normal")
            self.after(0, lambda m=msg, t=tipo: self.log(m, t))
            _orig(*args, **kw)

        builtins.print = _gui_print

        try:
            from pages.pedidos import executar_pedido
            from pages.pdf import baixar_pdf

            for i, pedido in enumerate(self.fila):
                if pedido["status"] != "pendente":
                    continue

                pedido["status"] = "rodando"
                self.after(0, self._atualizar_tree_fila)

                self.after(0, lambda n=i+1, c=pedido["dados"]["cliente"]:
                    self.log(f"\n{'─'*55}\n  PEDIDO {n}: {c.upper()}\n{'─'*55}", "info"))

                try:
                    codigo = executar_pedido(pedido["dados"], pedido["itens"])
                    pedido["codigo"] = codigo
                    pedido["status"] = "concluido"
                    self.after(0, self._atualizar_tree_fila)

                    # Adiciona à aba Conferir
                    self.after(0, lambda p=pedido, cd=codigo:
                        self.tree_conf.insert("", "end", values=(
                            cd or "—",
                            p["dados"]["cliente"],
                            p["dados"]["data"],
                            "Sim" if p["baixar_pdf"] else "Não")))

                    self.after(0, lambda c=codigo:
                        self.log(f"\n✔  Pedido concluído — Código: {c}", "ok"))

                    # PDF se solicitado
                    if pedido["baixar_pdf"] and codigo:
                        self.after(0, lambda c=codigo:
                            self.log(f"[PDF] Baixando pedido #{c}...", "info"))
                        try:
                            baixar_pdf(codigo, pedido["dados"]["cliente"],
                                       pedido["dados"]["data"])
                        except Exception as ex:
                            self.after(0, lambda e=str(ex):
                                self.log(f"[PDF] [ERRO] {e}", "erro"))

                except Exception as ex:
                    pedido["status"] = "erro"
                    self.after(0, self._atualizar_tree_fila)
                    self.after(0, lambda e=str(ex):
                        self.log(f"\n[ERRO] Pedido falhou: {e}", "erro"))

            concluidos = sum(1 for p in self.fila if p["status"] == "concluido")
            erros      = sum(1 for p in self.fila if p["status"] == "erro")
            self.after(0, lambda:
                self.log(f"\n{'═'*55}\n  FILA CONCLUÍDA — "
                         f"{concluidos} ok  |  {erros} com erro\n{'═'*55}", "info"))
            self.after(0, lambda: self._status("Fila concluída."))
            self.after(0, lambda:
                messagebox.showinfo("Fila Concluída",
                    f"{concluidos} pedido(s) criados com sucesso.\n"
                    + (f"{erros} com erro — verifique o log." if erros else "")
                    + "\n\nVá para a aba Conferir para liberar os pedidos quando seu pai pedir."))

        except Exception as ex:
            self.after(0, lambda e=str(ex):
                self.log(f"[ERRO FATAL] {e}", "erro"))
            self.after(0, lambda: self._status("Erro na fila."))
        finally:
            builtins.print = _orig

    # ── Conferir ─────────────────────────────

    def _remover_da_conferencia(self):
        sel = self.tree_conf.selection()
        for item in sel:
            self.tree_conf.delete(item)

    def _conferir_selecionados(self):
        sel = self.tree_conf.selection()
        if not sel:
            messagebox.showinfo("Nenhum selecionado",
                "Selecione um ou mais pedidos para conferir.\n"
                "(Use Ctrl+clique para selecionar vários)")
            return

        pedidos_sel = []
        for item in sel:
            vals = self.tree_conf.item(item, "values")
            codigo = vals[0]
            cliente = vals[1]
            if codigo and codigo != "—":
                pedidos_sel.append((codigo, cliente, item))

        if not pedidos_sel:
            messagebox.showwarning("Sem código",
                "Nenhum pedido selecionado tem código registrado.")
            return

        nomes = "\n".join(f"  #{c} — {cl}" for c, cl, _ in pedidos_sel)
        if not messagebox.askyesno("Confirmar Conferência",
            f"Confirmar os seguintes pedidos no sistema?\n\n{nomes}"):
            return

        self.nb.select(5)
        self.log(f"\n{'─'*55}", "info")
        self.log(f"  CONFERINDO {len(pedidos_sel)} pedido(s)...", "info")
        self._status("Conferindo pedidos...")

        itens_para_remover = [item for _, _, item in pedidos_sel]

        threading.Thread(
            target=self._rodar_conferencia,
            args=(pedidos_sel, itens_para_remover),
            daemon=True
        ).start()

    def _rodar_conferencia(self, pedidos_sel, itens_tree):
        import builtins
        _orig = builtins.print

        def _gui_print(*args, **kw):
            msg = " ".join(str(a) for a in args)
            tipo = "ok" if "[OK]" in msg else "erro" if "[ERRO]" in msg else "normal"
            self.after(0, lambda m=msg, t=tipo: self.log(m, t))
            _orig(*args, **kw)

        builtins.print = _gui_print

        try:
            from pages.pedidos import conferir_pedido

            ok_count = 0
            for codigo, cliente, tree_item in pedidos_sel:
                try:
                    conferir_pedido(codigo)
                    ok_count += 1
                    self.after(0, lambda c=codigo, cl=cliente:
                        self.log(f"  [OK] #{c} — {cl} conferido.", "ok"))
                    self.after(0, lambda ti=tree_item:
                        self.tree_conf.delete(ti))
                except Exception as ex:
                    self.after(0, lambda c=codigo, e=str(ex):
                        self.log(f"  [ERRO] #{c} — {e}", "erro"))

            self.after(0, lambda n=ok_count:
                self.log(f"\n✔  {n} pedido(s) conferidos.", "ok"))
            self.after(0, lambda: self._status("Conferência concluída."))
            self.after(0, lambda n=ok_count:
                messagebox.showinfo("Conferência Concluída",
                    f"{n} pedido(s) confirmados no sistema."))

        except Exception as ex:
            self.after(0, lambda e=str(ex):
                self.log(f"[ERRO FATAL] {e}", "erro"))
            self.after(0, lambda: self._status("Erro na conferência."))
        finally:
            builtins.print = _orig

    # ── Helpers de planilhas ──────────────────

    def _log_planilha(self, msg, tipo="info"):
        self.txt_planilha_resultado.configure(state="normal")
        self.txt_planilha_resultado.insert("end", msg + "\n", tipo)
        self.txt_planilha_resultado.see("end")
        self.txt_planilha_resultado.configure(state="disabled")

    def _escolher_arquivo(self, variavel, titulo):
        caminho = filedialog.askopenfilename(
            title=titulo,
            filetypes=[("Excel", "*.xlsx *.xlsm"), ("Todos", "*.*")])
        if caminho:
            variavel.set(caminho)

    def _salvar_caminhos_planilhas(self):
        cfg = _carregar_config()
        cfg["relatorio"]   = self.v_rel.get().strip()
        cfg["programacao"] = self.v_prog.get().strip()
        _salvar_config(cfg)
        messagebox.showinfo("Salvo", "Caminhos salvos com sucesso!")

    def _preencher_via_foto(self):
        caminho_foto = filedialog.askopenfilename(
            title="Selecione a foto do impresso",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos", "*.*")])
        if not caminho_foto: return

        rel  = self.v_rel.get().strip()
        prog = self.v_prog.get().strip()

        if not os.path.exists(rel):
            messagebox.showerror("Não encontrado",
                f"Relatório não encontrado:\n{rel}"); return
        if not os.path.exists(prog):
            messagebox.showerror("Não encontrado",
                f"Programação não encontrada:\n{prog}"); return

        self.txt_planilha_resultado.configure(state="normal")
        self.txt_planilha_resultado.delete("1.0", "end")
        self.txt_planilha_resultado.configure(state="disabled")

        self._log_planilha(f"Foto: {os.path.basename(caminho_foto)}", "info")
        self._log_planilha(f"Período: {self.v_periodo.get()}", "info")

        periodo = self.v_periodo.get()

        def _rodar():
            import sys
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if base not in sys.path:
                sys.path.insert(0, base)
            try:
                import preencher_planilhas as pp
                from pathlib import Path
                pp.RELATORIO   = Path(rel)
                pp.PROGRAMACAO = Path(prog)
                self.after(0, lambda: self._log_planilha("Lendo com IA...", "info"))
                dados = pp.extrair_dados_imagem(caminho_foto)
                self.after(0, lambda: self._log_planilha(
                    f"\n{len(dados)} cliente(s) detectados:", "info"))
                for d in dados:
                    m = f"  {d.get('cliente','?')}: {d.get('kg','?')} kg | R$ {d.get('valor_rs','?')}"
                    self.after(0, lambda msg=m: self._log_planilha(msg))
                self.after(0, lambda: self._log_planilha("\nAtualizando...", "info"))
                ok, nok = pp.atualizar_planilhas(dados, periodo)
                for n in ok:
                    self.after(0, lambda x=n: self._log_planilha(f"  ✔ {x}", "ok"))
                for n in nok:
                    self.after(0, lambda x=n: self._log_planilha(
                        f"  ⚠ {x} — não encontrado", "aviso"))
                self.after(0, lambda: self._log_planilha("\nPlanilhas salvas!", "ok"))
                self.after(0, lambda: messagebox.showinfo("Concluído",
                    f"{len(ok)} cliente(s) atualizados."))
            except Exception as ex:
                self.after(0, lambda e=str(ex): self._log_planilha(f"[ERRO] {e}", "erro"))
                self.after(0, lambda: messagebox.showerror("Erro", str(ex)))

        threading.Thread(target=_rodar, daemon=True).start()


# ── Ponto de entrada ─────────────────────────
if __name__ == "__main__":
    App().mainloop()