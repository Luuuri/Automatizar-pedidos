# ─────────────────────────────────────────────
#  pages/interface.py — interface gráfica Tkinter
#  Visual inspirado no sistema SGEP (tema claro)
#  Execute: python main.py
# ─────────────────────────────────────────────

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import date
import os
import json

from config import TODOS_CLIENTES, PAGAMENTOS, ESPECIES

# ── Caminhos de dados ─────────────────────────
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(_BASE, "data", "log.txt")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# ── Paleta SGEP (tema claro) ──────────────────
COR = {
    "janela":      "#f0f2f5",   # fundo geral acinzentado
    "fundo":       "#ffffff",   # fundo dos cards/painéis
    "borda":       "#d0d7de",   # borda sutil
    "borda_focus": "#2c7be5",   # azul SGEP no foco
    "acento":      "#2c5f8a",   # azul escuro cabeçalho/abas
    "acento_btn":  "#3a7abf",   # azul botão primário
    "acento_hov":  "#2c6aa0",   # hover do botão
    "texto":       "#1a2535",   # quase preto
    "texto_fraco": "#6b7a8d",   # cinza para labels/hints
    "texto_branco":"#ffffff",
    "verde":       "#1a7f4e",
    "verde_bg":    "#d4edda",
    "vermelho":    "#b02020",
    "vermelho_bg": "#f8d7da",
    "amarelo":     "#856404",
    "amarelo_bg":  "#fff3cd",
    "linha_tab":   "#e3e8ef",   # separador de linhas na tabela
    "aba_inativa": "#dce3ec",
    "aba_ativa":   "#ffffff",
    "cabecalho":   "#1e3a5f",   # azul escuro do topo
    "rodape":      "#e8ecf0",
}

FONTE_LABEL  = ("Segoe UI", 9)
FONTE_INPUT  = ("Segoe UI", 10)
FONTE_BTN    = ("Segoe UI", 9, "bold")
FONTE_LOG    = ("Consolas", 8)
FONTE_CABEC  = ("Segoe UI", 13, "bold")
FONTE_TITULO = ("Segoe UI", 10, "bold")

# ── Widgets estilo SGEP ───────────────────────

def _aplicar_estilos():
    s = ttk.Style()
    s.theme_use("clam")

    # Notebook / abas
    s.configure("SGEP.TNotebook",
        background=COR["janela"], borderwidth=0, tabmargins=[0, 0, 0, 0])
    s.configure("SGEP.TNotebook.Tab",
        background=COR["aba_inativa"], foreground=COR["texto_fraco"],
        font=("Segoe UI", 9, "bold"), padding=[16, 6], borderwidth=1,
        relief="flat")
    s.map("SGEP.TNotebook.Tab",
        background=[("selected", COR["aba_ativa"])],
        foreground=[("selected", COR["acento"])],
        expand=[("selected", [1, 1, 1, 0])])

    # Combobox
    s.configure("SGEP.TCombobox",
        fieldbackground=COR["fundo"], background=COR["fundo"],
        foreground=COR["texto"], selectbackground=COR["acento_btn"],
        selectforeground=COR["texto_branco"], arrowcolor=COR["acento_btn"],
        bordercolor=COR["borda"], lightcolor=COR["borda"],
        darkcolor=COR["borda"], relief="solid")
    s.map("SGEP.TCombobox",
        fieldbackground=[("readonly", COR["fundo"])],
        foreground=[("readonly", COR["texto"])],
        bordercolor=[("focus", COR["borda_focus"])])

    # Treeview
    s.configure("SGEP.Treeview",
        background=COR["fundo"], foreground=COR["texto"],
        fieldbackground=COR["fundo"], borderwidth=1,
        font=FONTE_INPUT, rowheight=28, relief="solid")
    s.configure("SGEP.Treeview.Heading",
        background=COR["acento"], foreground=COR["texto_branco"],
        font=("Segoe UI", 9, "bold"), borderwidth=0, relief="flat", padding=6)
    s.map("SGEP.Treeview",
        background=[("selected", COR["acento_btn"])],
        foreground=[("selected", COR["texto_branco"])])

    # Scrollbar
    s.configure("SGEP.Vertical.TScrollbar",
        background=COR["borda"], troughcolor=COR["janela"],
        arrowcolor=COR["texto_fraco"], borderwidth=0, relief="flat")


def _entry(parent, var=None, width=24, readonly=False, **kw):
    state = "readonly" if readonly else "normal"
    e = tk.Entry(parent, textvariable=var, font=FONTE_INPUT,
                 bg=COR["fundo"] if not readonly else COR["janela"],
                 fg=COR["texto"] if not readonly else COR["texto_fraco"],
                 disabledforeground=COR["texto_fraco"],
                 disabledbackground=COR["janela"],
                 insertbackground=COR["acento_btn"],
                 relief="solid", bd=1,
                 highlightthickness=1,
                 highlightbackground=COR["borda"],
                 highlightcolor=COR["borda_focus"],
                 width=width, **kw)
    if readonly:
        e.configure(state="disabled")
    return e


def _combo(parent, values, var=None, width=22):
    c = ttk.Combobox(parent, values=values, textvariable=var,
                     font=FONTE_INPUT, style="SGEP.TCombobox",
                     width=width, state="normal")
    return c


def _label(parent, texto, fraco=False, bold=False, bg=None, **kw):
    fonte = ("Segoe UI", 9, "bold") if bold else FONTE_LABEL
    return tk.Label(parent, text=texto, font=fonte,
                    bg=bg or COR["fundo"],
                    fg=COR["texto_fraco"] if fraco else COR["texto"], **kw)


def _btn_primario(parent, texto, cmd, **kw):
    """Botão azul principal (estilo Gravar do SGEP)."""
    return tk.Button(parent, text=texto, command=cmd,
                     font=FONTE_BTN,
                     bg=COR["acento_btn"], fg=COR["texto_branco"],
                     activebackground=COR["acento_hov"],
                     activeforeground=COR["texto_branco"],
                     relief="flat", cursor="hand2",
                     padx=14, pady=5, **kw)


def _btn_secundario(parent, texto, cmd, **kw):
    """Botão cinza secundário (estilo Limpar do SGEP)."""
    return tk.Button(parent, text=texto, command=cmd,
                     font=FONTE_BTN,
                     bg=COR["borda"], fg=COR["texto"],
                     activebackground="#bec8d4",
                     activeforeground=COR["texto"],
                     relief="flat", cursor="hand2",
                     padx=14, pady=5, **kw)


def _separador(parent, vertical=False):
    orient = "vertical" if vertical else "horizontal"
    return tk.Frame(parent,
                    bg=COR["borda"],
                    width=1 if vertical else 0,
                    height=0 if vertical else 1)


def _card(parent, titulo=None, **kw):
    """Frame com borda e título opcional (como os painéis do SGEP)."""
    outer = tk.Frame(parent, bg=COR["borda"], bd=0, **kw)
    inner = tk.Frame(outer, bg=COR["fundo"], bd=0)
    inner.pack(fill="both", expand=True, padx=1, pady=1)

    if titulo:
        tit = tk.Frame(inner, bg=COR["acento"], height=28)
        tit.pack(fill="x")
        tk.Label(tit, text=f"  {titulo}", font=("Segoe UI", 9, "bold"),
                 bg=COR["acento"], fg=COR["texto_branco"]).pack(side="left", pady=4)
        corpo = tk.Frame(inner, bg=COR["fundo"])
        corpo.pack(fill="both", expand=True)
        return outer, corpo
    return outer, inner


def _linha_form(parent, label, widget, row, col_start=0, hint=None):
    """Label + widget numa grade de formulário."""
    lbl = _label(parent, label, fraco=True)
    lbl.grid(row=row, column=col_start, sticky="w",
             padx=(12, 6), pady=(8, 1))
    widget.grid(row=row, column=col_start + 1, sticky="ew",
                padx=(0, 12), pady=(8, 1))
    if hint:
        _label(parent, hint, fraco=True).grid(
            row=row + 1, column=col_start + 1, sticky="w",
            padx=(0, 12), pady=(0, 2))


def _filtrar(combo, lista, digitado):
    f = [x for x in lista if digitado.lower() in x.lower()]
    combo["values"] = f if f else lista


# ── Persistência do log ───────────────────────

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


# ── App principal ─────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SGEP — Automação de Pedidos")
        self.configure(bg=COR["janela"])
        self.resizable(True, True)
        self.minsize(820, 680)
        self.geometry("900x720")

        # variável para guardar o código do pedido criado (para o PDF)
        self._codigo_pedido = None
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

    # ── Layout geral ─────────────────────────

    def _build(self):
        # ── Cabeçalho estilo SGEP ──
        cab = tk.Frame(self, bg=COR["cabecalho"], height=48)
        cab.pack(fill="x")
        cab.pack_propagate(False)

        tk.Label(cab, text="🐟  SGEP — Automação de Pedidos",
                 font=FONTE_CABEC, bg=COR["cabecalho"],
                 fg=COR["texto_branco"]).pack(side="left", padx=16, pady=10)

        tk.Label(cab, text="Americo Lima  |  AMASA Belém",
                 font=FONTE_LABEL, bg=COR["cabecalho"],
                 fg="#8daac8").pack(side="right", padx=16)

        # ── Abas ──
        self.nb = ttk.Notebook(self, style="SGEP.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._aba_pedido()
        self._aba_itens()
        self._aba_log()

        # ── Rodapé ──
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
        self.nb.add(frame, text="  Pedidos  ")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        # ── Bloco superior: campos principais ──
        outer, corpo = _card(frame, titulo="Informações do Pedido")
        outer.grid(row=0, column=0, columnspan=2,
                   sticky="ew", padx=12, pady=(10, 6))
        corpo.columnconfigure(1, weight=1)
        corpo.columnconfigure(3, weight=1)

        # Linha 0: Ordem Compra | Data
        self.v_ordem = tk.StringVar(value="0")
        _label(corpo, "Ordem Compra", fraco=True).grid(
            row=0, column=0, sticky="w", padx=(12, 6), pady=(10, 2))
        _entry(corpo, self.v_ordem, width=14).grid(
            row=0, column=1, sticky="w", padx=(0, 20), pady=(10, 2))

        self.v_data = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        _label(corpo, "Prev. Entrega", fraco=True).grid(
            row=0, column=2, sticky="w", padx=(0, 6), pady=(10, 2))
        _entry(corpo, self.v_data, width=14).grid(
            row=0, column=3, sticky="w", padx=(0, 12), pady=(10, 2))

        # Linha 1: Empresa (fixo)
        self.v_empresa = tk.StringVar(
            value="AMAZONAS INDUSTRIAS ALIMENTICIAS S A AMASA — BELÉM")
        _label(corpo, "Empresa", fraco=True).grid(
            row=1, column=0, sticky="w", padx=(12, 6), pady=(6, 2))
        _entry(corpo, self.v_empresa, width=52, readonly=True).grid(
            row=1, column=1, columnspan=3, sticky="ew",
            padx=(0, 12), pady=(6, 2))

        # Linha 2: Cliente
        self.v_cliente = tk.StringVar()
        _label(corpo, "Cliente", fraco=True).grid(
            row=2, column=0, sticky="w", padx=(12, 6), pady=(6, 2))
        cb_cli = _combo(corpo, TODOS_CLIENTES, self.v_cliente, width=40)
        cb_cli.bind("<KeyRelease>",
                    lambda e: _filtrar(cb_cli, TODOS_CLIENTES, self.v_cliente.get()))
        cb_cli.grid(row=2, column=1, columnspan=3, sticky="ew",
                    padx=(0, 12), pady=(6, 2))

        # Linha 3: Vendedor (fixo) | Cond Pagamento
        self.v_vendedor = tk.StringVar(value="Americo Lima  (único disponível)")
        _label(corpo, "Vendedor", fraco=True).grid(
            row=3, column=0, sticky="w", padx=(12, 6), pady=(6, 2))
        _entry(corpo, self.v_vendedor, width=28, readonly=True).grid(
            row=3, column=1, sticky="ew", padx=(0, 20), pady=(6, 2))

        self.v_pagto = tk.StringVar()
        _label(corpo, "Cond. Pagto", fraco=True).grid(
            row=3, column=2, sticky="w", padx=(0, 6), pady=(6, 2))
        cb_pag = _combo(corpo, PAGAMENTOS, self.v_pagto, width=18)
        cb_pag.bind("<KeyRelease>",
                    lambda e: _filtrar(cb_pag, PAGAMENTOS, self.v_pagto.get()))
        cb_pag.grid(row=3, column=3, sticky="ew", padx=(0, 12), pady=(6, 2))

        # Linha 4: Observações
        _label(corpo, "Observações", fraco=True).grid(
            row=4, column=0, sticky="nw", padx=(12, 6), pady=(6, 2))
        self.txt_obs = tk.Text(
            corpo, font=FONTE_INPUT, bg=COR["fundo"], fg=COR["texto"],
            insertbackground=COR["acento_btn"],
            relief="solid", bd=1, width=52, height=3, wrap="word")
        self.txt_obs.grid(row=4, column=1, columnspan=3, sticky="ew",
                          padx=(0, 12), pady=(6, 8))

        # ── Opção de PDF ──
        outer_pdf, corpo_pdf = _card(frame, titulo="Opções")
        outer_pdf.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 10))
        corpo_pdf.columnconfigure(0, weight=1)

        self.v_baixar_pdf = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(
            corpo_pdf,
            text="Baixar PDF do pedido após criar",
            variable=self.v_baixar_pdf,
            font=FONTE_INPUT,
            bg=COR["fundo"], fg=COR["texto"],
            activebackground=COR["fundo"],
            selectcolor=COR["fundo"],
            cursor="hand2")
        chk.pack(anchor="w", padx=12, pady=(10, 4))

        _label(corpo_pdf,
               "O sistema buscará o pedido pelo código gerado\n"
               "e salvará o PDF automaticamente na pasta data/pedidos/",
               fraco=True).pack(anchor="w", padx=12, pady=(0, 10))

        # ── Botões ──
        outer_btn, corpo_btn = _card(frame, titulo="")
        outer_btn.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 10))

        _btn_primario(corpo_btn, "  Ir para Itens  →",
                      lambda: self.nb.select(1)).pack(
            pady=(20, 8), padx=16, fill="x")
        _btn_secundario(corpo_btn, "  Limpar Formulário",
                        self._limpar_pedido).pack(
            pady=(0, 8), padx=16, fill="x")

    # ── Aba 2 — Itens Pedidos ────────────────

    def _aba_itens(self):
        frame = tk.Frame(self.nb, bg=COR["janela"])
        self.nb.add(frame, text="  Itens Pedidos  ")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # ── Formulário de item ──
        outer, corpo = _card(frame, titulo="Novo Item")
        outer.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
        corpo.columnconfigure(1, weight=1)
        corpo.columnconfigure(3, weight=1)
        corpo.columnconfigure(5, weight=1)

        # Linha 0: Espécie | PA | Quantidade | Valor
        self.v_esp = tk.StringVar()
        _label(corpo, "Espécie", fraco=True).grid(
            row=0, column=0, sticky="w", padx=(12, 6), pady=(10, 2))
        cb_esp = _combo(corpo, ESPECIES, self.v_esp, width=14)
        cb_esp.bind("<KeyRelease>",
                    lambda e: _filtrar(cb_esp, ESPECIES, self.v_esp.get()))
        cb_esp.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=(10, 2))

        self.v_pa = tk.StringVar()
        _label(corpo, "PA", fraco=True).grid(
            row=0, column=2, sticky="w", padx=(0, 6), pady=(10, 2))
        _entry(corpo, self.v_pa, width=8).grid(
            row=0, column=3, sticky="w", padx=(0, 16), pady=(10, 2))

        self.v_qtd = tk.StringVar()
        _label(corpo, "Qtd (kg)", fraco=True).grid(
            row=0, column=4, sticky="w", padx=(0, 6), pady=(10, 2))
        _entry(corpo, self.v_qtd, width=10).grid(
            row=0, column=5, sticky="ew", padx=(0, 16), pady=(10, 2))

        self.v_val = tk.StringVar()
        _label(corpo, "Valor Unit.", fraco=True).grid(
            row=0, column=6, sticky="w", padx=(0, 6), pady=(10, 2))
        _entry(corpo, self.v_val, width=10).grid(
            row=0, column=7, sticky="ew", padx=(0, 12), pady=(10, 2))

        # Linha 1: hint + botão
        _label(corpo, "Uni. Medida sempre KG — valor comparado com o sistema automaticamente",
               fraco=True).grid(
            row=1, column=0, columnspan=6, sticky="w", padx=(12, 0), pady=(0, 6))

        _btn_primario(corpo, "+ Adicionar", self._add_item).grid(
            row=1, column=6, columnspan=2, padx=(0, 12), pady=(0, 8), sticky="e")

        # ── Tabela de itens ──
        outer_t, corpo_t = _card(frame, titulo="Itens do Pedido")
        outer_t.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 6))
        corpo_t.columnconfigure(0, weight=1)
        corpo_t.rowconfigure(0, weight=1)

        cols = ("Espécie", "PA", "Qtd (kg)", "Valor Solicitado")
        self.tree = ttk.Treeview(corpo_t, columns=cols, show="headings",
                                  style="SGEP.Treeview", height=8)
        for col, w in zip(cols, (180, 80, 100, 120)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(corpo_t, orient="vertical",
                           command=self.tree.yview,
                           style="SGEP.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        sb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0, 4))

        # ── Botões finais ──
        btn_row = tk.Frame(frame, bg=COR["janela"])
        btn_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

        _btn_secundario(btn_row, "✕  Remover Item", self._remover).pack(
            side="left", padx=(0, 8))
        _btn_primario(btn_row, "▶  Gravar e Executar Pedido",
                      self._executar).pack(side="right")
        _btn_secundario(btn_row, "← Voltar ao Pedido",
                        lambda: self.nb.select(0)).pack(side="right", padx=(0, 8))

    # ── Aba 3 — Log ──────────────────────────

    def _aba_log(self):
        frame = tk.Frame(self.nb, bg=COR["janela"])
        self.nb.add(frame, text="  Log  ")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        outer, corpo = _card(frame, titulo="Histórico de Execuções")
        outer.grid(row=0, column=0, sticky="nsew", padx=12, pady=(10, 6))
        corpo.columnconfigure(0, weight=1)
        corpo.rowconfigure(0, weight=1)

        self.log_txt = tk.Text(
            corpo, font=FONTE_LOG,
            bg="#1a1e2e", fg="#c8d3e0",
            insertbackground=COR["acento_btn"],
            relief="flat", state="disabled", wrap="word")
        sb = ttk.Scrollbar(corpo, orient="vertical",
                           command=self.log_txt.yview,
                           style="SGEP.Vertical.TScrollbar")
        self.log_txt.configure(yscrollcommand=sb.set)
        self.log_txt.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        sb.grid(row=0, column=1, sticky="ns", pady=6, padx=(0, 4))

        self.log_txt.tag_config("ok",     foreground="#4ade80")
        self.log_txt.tag_config("erro",   foreground="#f87171")
        self.log_txt.tag_config("aviso",  foreground="#fbbf24")
        self.log_txt.tag_config("info",   foreground="#60a5fa")
        self.log_txt.tag_config("normal", foreground="#c8d3e0")

        # botão limpar log
        btn_row = tk.Frame(frame, bg=COR["janela"])
        btn_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        _btn_secundario(btn_row, "Limpar Log", self._limpar_log).pack(side="right")
        tk.Button(
            btn_row, text="📎  Enviar PDF via WhatsApp",
            command=self._enviar_whatsapp,
            font=FONTE_BTN,
            bg="#25D366", fg="white",
            activebackground="#1ebe57",
            activeforeground="white",
            relief="flat", cursor="hand2",
            padx=14, pady=5
        ).pack(side="left")

    # ── Helpers ──────────────────────────────

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
        if messagebox.askyesno("Limpar Log", "Apagar todo o histórico de log?"):
            self.log_txt.configure(state="normal")
            self.log_txt.delete("1.0", "end")
            self.log_txt.configure(state="disabled")
            try:
                open(LOG_PATH, "w").close()
            except Exception:
                pass

    def _limpar_pedido(self):
        self.v_ordem.set("0")
        self.v_data.set(date.today().strftime("%d/%m/%Y"))
        self.v_cliente.set("")
        self.v_pagto.set("")
        self.txt_obs.delete("1.0", "end")

    def _add_item(self):
        esp = self.v_esp.get().strip().lower()
        pa  = self.v_pa.get().strip().zfill(4)
        qtd = self.v_qtd.get().strip().replace(",", ".")
        val = self.v_val.get().strip().replace(",", ".")

        if not esp:
            messagebox.showwarning("Campo vazio", "Preencha a Espécie."); return
        if pa == "0000":
            messagebox.showwarning("Campo vazio", "Preencha o PA do produto."); return
        try:
            qtd_f = float(qtd)
        except ValueError:
            messagebox.showerror("Inválido", "Quantidade deve ser um número."); return
        try:
            val_f = float(val)
        except ValueError:
            messagebox.showerror("Inválido", "Valor deve ser um número."); return

        self.itens.append({"especie": esp, "pa": pa, "quantidade": qtd_f, "valor": val_f})
        self.tree.insert("", "end", values=(
            esp.capitalize(), pa,
            f"{qtd_f:.3f}".rstrip("0").rstrip("."),
            f"R$ {val_f:.2f}"
        ))
        self.v_esp.set(""); self.v_pa.set("")
        self.v_qtd.set(""); self.v_val.set("")

    def _remover(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        self.tree.delete(sel[0])
        self.itens.pop(idx)

    def _validar(self):
        erros = []
        if not self.v_ordem.get().strip(): erros.append("Ordem de Compra")
        if not self.v_data.get().strip():  erros.append("Data de Entrega")
        if not self.v_cliente.get().strip(): erros.append("Cliente")
        if not self.v_pagto.get().strip():   erros.append("Cond. Pagamento")
        if not self.itens: erros.append("Nenhum item adicionado")
        return erros

    def _executar(self):
        erros = self._validar()
        if erros:
            messagebox.showerror("Campos obrigatórios",
                "Preencha antes de continuar:\n\n• " + "\n• ".join(erros))
            return

        baixar = self.v_baixar_pdf.get()
        msg = (f"Cliente:  {self.v_cliente.get()}\n"
               f"Data:     {self.v_data.get()}\n"
               f"Itens:    {len(self.itens)}\n"
               f"PDF:      {'Sim' if baixar else 'Não'}\n\n"
               "Iniciar automação?")
        if not messagebox.askyesno("Confirmar", msg):
            return

        self.nb.select(2)
        self.log("═" * 55, "info")
        self.log(f"  NOVO PEDIDO — {date.today().strftime('%d/%m/%Y %H:%M')}", "info")
        self.log("═" * 55, "info")
        self._status("Automação em andamento...")

        threading.Thread(target=self._rodar, daemon=True).start()

    def _rodar(self):
        import builtins
        _orig = builtins.print

        def _gui_print(*args, **kw):
            msg = " ".join(str(a) for a in args)
            tipo = ("ok"    if "[OK]"     in msg else
                    "erro"  if "[ERRO]"   in msg or "[PULADO]" in msg else
                    "aviso" if "[AVISO]"  in msg or "INFERIOR" in msg else
                    "normal")
            self.after(0, lambda m=msg, t=tipo: self.log(m, t))
            _orig(*args, **kw)

        builtins.print = _gui_print

        try:
            from pages.pedidos import executar_pedido

            dados = {
                "ordem":          self.v_ordem.get().strip(),
                "data":           self.v_data.get().strip(),
                "cliente":        self.v_cliente.get().strip().lower(),
                "pagamento":      self.v_pagto.get().strip().lower(),
                "observacao":     self.txt_obs.get("1.0", "end").strip(),
                "empresa_index":  1,
                "vendedor_index": 1,
            }

            codigo = executar_pedido(dados, self.itens)
            self._codigo_pedido = codigo

            self.after(0, lambda: self.log("\n✔  PEDIDO CONCLUÍDO!", "ok"))
            self.after(0, lambda: self._status("Pedido concluído."))

            # ── PDF (opcional) ──────────────────
            if self.v_baixar_pdf.get():
                if codigo:
                    self.after(0, lambda: self.log(
                        f"\n[PDF] Buscando pedido #{codigo}...", "info"))
                    self._baixar_pdf(codigo, dados["cliente"], dados["data"])
                else:
                    self.after(0, lambda: self.log(
                        "[PDF] Código do pedido não capturado — baixe manualmente.", "aviso"))

            self.after(0, lambda: messagebox.showinfo(
                "Concluído", "Pedido enviado com sucesso!\nVerifique o sistema."))

        except Exception as ex:
            self.after(0, lambda e=str(ex): self.log(f"[ERRO FATAL] {e}", "erro"))
            self.after(0, lambda: self._status("Erro na automação."))
            self.after(0, lambda: messagebox.showerror("Erro na automação", str(ex)))
        finally:
            builtins.print = _orig

    def _baixar_pdf(self, codigo, cliente, data):
        """Chama pages/pdf.py para baixar o PDF com valor do pedido."""
        try:
            from pages.pdf import baixar_pdf
            ok = baixar_pdf(codigo, cliente, data)
            if ok:
                self.after(0, lambda: self.log(
                    f"[PDF] [OK] PDF do pedido #{codigo} salvo em data/pedidos/", "ok"))
            else:
                self.after(0, lambda: self.log(
                    f"[PDF] [AVISO] Não foi possível salvar automaticamente. Veja o log acima.", "aviso"))
        except ImportError:
            self.after(0, lambda: self.log(
                "[PDF] [AVISO] Instale as dependências: pip install pyautogui pyperclip keyboard", "aviso"))
        except Exception as ex:
            self.after(0, lambda e=str(ex): self.log(f"[PDF] [ERRO] {e}", "erro"))


    def _enviar_whatsapp(self):
        """Abre seletor de arquivo na pasta de pedidos e envia via WhatsApp Web."""
        from pages.whatsapp import enviar_pdf, PASTA_PDF

        # Abre o explorador de arquivos já na pasta certa, filtrando só PDFs
        caminho = filedialog.askopenfilename(
            title="Selecione o PDF para enviar",
            initialdir=PASTA_PDF,
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")]
        )
        if not caminho:
            return  # usuário cancelou

        self.nb.select(2)  # vai para aba Log
        self.log(f"[WA] Enviando: {os.path.basename(caminho)}", "info")

        def _rodar_wa():
            try:
                enviar_pdf(caminho)
                self.after(0, lambda: self.log("[WA] [OK] PDF enviado com sucesso!", "ok"))
                self.after(0, lambda: messagebox.showinfo(
                    "WhatsApp", "PDF enviado para Pai Américo!"))
            except Exception as ex:
                self.after(0, lambda e=str(ex): self.log(f"[WA] [ERRO] {e}", "erro"))
                self.after(0, lambda: messagebox.showerror("Erro WhatsApp", str(ex)))

        threading.Thread(target=_rodar_wa, daemon=True).start()


# ── Ponto de entrada ─────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()