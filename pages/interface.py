import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import date

# ─────────────────────────────────────────────
#  PALETA & FONTES
# ─────────────────────────────────────────────
COR = {
    "fundo":        "#0f1923",   # azul-noite profundo
    "painel":       "#162332",   # card levemente mais claro
    "borda":        "#1e3448",   # borda sutil
    "acento":       "#00b4d8",   # azul-água (cor principal de destaque)
    "acento2":      "#0077a8",   # azul mais escuro para hover/pressed
    "texto":        "#e8f4f8",   # quase branco com tom frio
    "texto_fraco":  "#6b8fa3",   # cinza-azulado para labels
    "verde":        "#22c55e",
    "vermelho":     "#ef4444",
    "amarelo":      "#f59e0b",
    "linha":        "#1e3448",
}

FONTE_TITULO  = ("Consolas", 13, "bold")
FONTE_LABEL   = ("Consolas", 9)
FONTE_INPUT   = ("Consolas", 10)
FONTE_BTN     = ("Consolas", 10, "bold")
FONTE_LOG     = ("Consolas", 8)
FONTE_CABEC   = ("Consolas", 16, "bold")

# ─────────────────────────────────────────────
#  DADOS FIXOS
# ─────────────────────────────────────────────
CLIENTES_ESPECIAIS = {
    "formosa_d":    {"busca": "formosa",       "value": "328"},
    "formosa_cn":   {"busca": "formosa",       "value": "327"},
    "formosa_agm":  {"busca": "formosa",       "value": "332"},
    "formosa_cu":   {"busca": "formosa",       "value": "329"},
    "formosa_g":    {"busca": "formosa",       "value": "9180"},
    "rest_cortizu": {"busca": "cortizu",       "value": "5860"},
    "mc_solano":    {"busca": "mc solano",     "value": "9411"},
    "trs":          {"busca": "trs de souza",  "value": "9410"},
    "s_alb":        {"busca": "s albuquerque", "value": "409"},
    "fas":          {"busca": "fas queiroz",   "value": "595"},
    "ds":           {"busca": "ds muller",     "value": "330"},
}
CLIENTES_NORMAIS = sorted([
    "compespa", "assembleia", "jo", "lucelia", "lider",
    "cambuci", "r3x", "shopping", "kenko", "amazonia", "dumar"
])
TODOS_CLIENTES = sorted(list(CLIENTES_ESPECIAIS.keys()) + CLIENTES_NORMAIS)

PAGAMENTOS = [
    "a vista", "contrato", "7 dias", "14 dias", "21 dias", "28 dias",
    "28/42", "30 dias", "30/60", "30/60/90", "45 dias", "60 dias",
]

ESPECIES = ["camarao", "dourada", "filhote", "jaraqui", "pirarucu",
            "pescada", "surubim", "tambaqui", "tucunare", "outros"]

# ─────────────────────────────────────────────
#  WIDGETS CUSTOMIZADOS
# ─────────────────────────────────────────────

def estilo_entry(parent, textvariable=None, width=28, **kw):
    e = tk.Entry(
        parent,
        textvariable=textvariable,
        font=FONTE_INPUT,
        bg=COR["fundo"],
        fg=COR["texto"],
        insertbackground=COR["acento"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=COR["borda"],
        highlightcolor=COR["acento"],
        width=width,
        **kw
    )
    return e

def estilo_combo(parent, values, textvariable=None, width=26, **kw):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.TCombobox",
        fieldbackground=COR["fundo"],
        background=COR["borda"],
        foreground=COR["texto"],
        selectbackground=COR["acento2"],
        selectforeground=COR["texto"],
        arrowcolor=COR["acento"],
        bordercolor=COR["borda"],
        lightcolor=COR["borda"],
        darkcolor=COR["borda"],
    )
    style.map("Dark.TCombobox",
        fieldbackground=[("readonly", COR["fundo"])],
        foreground=[("readonly", COR["texto"])],
    )
    c = ttk.Combobox(
        parent,
        values=values,
        textvariable=textvariable,
        font=FONTE_INPUT,
        style="Dark.TCombobox",
        width=width,
        state="normal",
        **kw
    )
    return c

def estilo_label(parent, texto, fraco=False, **kw):
    return tk.Label(
        parent,
        text=texto,
        font=FONTE_LABEL,
        bg=COR["painel"],
        fg=COR["texto_fraco"] if fraco else COR["texto"],
        **kw
    )

def estilo_btn(parent, texto, comando, cor=None, **kw):
    cor_bg = cor or COR["acento"]
    b = tk.Button(
        parent,
        text=texto,
        command=comando,
        font=FONTE_BTN,
        bg=cor_bg,
        fg=COR["fundo"],
        activebackground=COR["acento2"],
        activeforeground=COR["texto"],
        relief="flat",
        cursor="hand2",
        padx=16,
        pady=6,
        **kw
    )
    return b

def card(parent, **kw):
    return tk.Frame(parent, bg=COR["painel"],
                    highlightthickness=1,
                    highlightbackground=COR["borda"], **kw)

def linha_form(parent, label, widget, row):
    estilo_label(parent, label, fraco=True).grid(
        row=row, column=0, sticky="w", padx=(16, 8), pady=(8, 2))
    widget.grid(row=row, column=1, sticky="ew", padx=(0, 16), pady=(8, 2))

# ─────────────────────────────────────────────
#  JANELA PRINCIPAL
# ─────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SGEP — Automação de Pedidos")
        self.configure(bg=COR["fundo"])
        self.resizable(False, False)
        self.geometry("680x780")

        self.itens = []          # lista de dicts {especie, pa, quantidade, valor}
        self._build_ui()
        self._centralizar()

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── cabeçalho ──────────────────────────────
    def _build_ui(self):
        cab = tk.Frame(self, bg=COR["fundo"])
        cab.pack(fill="x", padx=24, pady=(20, 4))

        tk.Label(cab, text="◈  SGEP PEDIDOS", font=FONTE_CABEC,
                 bg=COR["fundo"], fg=COR["acento"]).pack(side="left")
        tk.Label(cab, text="automação de pescados", font=FONTE_LABEL,
                 bg=COR["fundo"], fg=COR["texto_fraco"]).pack(side="left", padx=(10, 0), pady=(6, 0))

        sep = tk.Frame(self, bg=COR["borda"], height=1)
        sep.pack(fill="x", padx=24, pady=(4, 12))

        # notebook
        nb_style = ttk.Style()
        nb_style.theme_use("clam")
        nb_style.configure("Dark.TNotebook",
            background=COR["fundo"], borderwidth=0, tabmargins=0)
        nb_style.configure("Dark.TNotebook.Tab",
            background=COR["borda"], foreground=COR["texto_fraco"],
            font=FONTE_BTN, padding=(18, 8), borderwidth=0)
        nb_style.map("Dark.TNotebook.Tab",
            background=[("selected", COR["painel"])],
            foreground=[("selected", COR["acento"])],
        )

        self.nb = ttk.Notebook(self, style="Dark.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self._aba_pedido()
        self._aba_itens()
        self._aba_log()

    # ── aba 1: pedido ──────────────────────────
    def _aba_pedido(self):
        frame = tk.Frame(self.nb, bg=COR["fundo"])
        self.nb.add(frame, text="  Pedido  ")

        c = card(frame)
        c.pack(fill="both", expand=True, padx=0, pady=8)
        c.columnconfigure(1, weight=1)

        # Ordem de Compra
        self.v_ordem = tk.StringVar(value="0")
        linha_form(c, "Ordem de Compra", estilo_entry(c, self.v_ordem), 0)

        # Empresa (padrão fixo, editável se necessário)
        self.v_empresa = tk.StringVar(value="AMASA — índice 1 (padrão)")
        emp_entry = estilo_entry(c, self.v_empresa, state="disabled",
                                  disabledforeground=COR["texto_fraco"],
                                  disabledbackground=COR["fundo"])
        linha_form(c, "Empresa", emp_entry, 1)
        estilo_label(c, "Sempre a primeira opção (AMASA Belém)", fraco=True).grid(
            row=2, column=1, sticky="w", padx=(0, 16))

        # Data de entrega
        hoje = date.today().strftime("%d/%m/%Y")
        self.v_data = tk.StringVar(value=hoje)
        linha_form(c, "Data de Entrega", estilo_entry(c, self.v_data), 3)
        estilo_label(c, "Formato  DD/MM/AAAA", fraco=True).grid(
            row=4, column=1, sticky="w", padx=(0, 16))

        # Cliente
        self.v_cliente = tk.StringVar()
        combo_cli = estilo_combo(c, TODOS_CLIENTES, self.v_cliente)
        combo_cli.bind("<KeyRelease>", lambda e: self._filtrar_combo(
            combo_cli, TODOS_CLIENTES, self.v_cliente.get()))
        linha_form(c, "Cliente", combo_cli, 5)

        # Cond. Pagamento
        self.v_pagto = tk.StringVar()
        combo_pag = estilo_combo(c, PAGAMENTOS, self.v_pagto)
        combo_pag.bind("<KeyRelease>", lambda e: self._filtrar_combo(
            combo_pag, PAGAMENTOS, self.v_pagto.get()))
        linha_form(c, "Cond. Pagamento", combo_pag, 6)

        # Observações
        estilo_label(c, "Observações", fraco=True).grid(
            row=7, column=0, sticky="nw", padx=(16, 8), pady=(12, 2))
        self.txt_obs = tk.Text(
            c, font=FONTE_INPUT, bg=COR["fundo"], fg=COR["texto"],
            insertbackground=COR["acento"], relief="flat",
            highlightthickness=1, highlightbackground=COR["borda"],
            highlightcolor=COR["acento"],
            width=30, height=4, wrap="word"
        )
        self.txt_obs.grid(row=7, column=1, sticky="ew",
                          padx=(0, 16), pady=(12, 2))
        estilo_label(c, "Opcional — VIA NAVIO, CONTRATO, etc.", fraco=True).grid(
            row=8, column=1, sticky="w", padx=(0, 16))

        # Vendedor (padrão fixo)
        estilo_label(c, "Vendedor", fraco=True).grid(
            row=9, column=0, sticky="w", padx=(16, 8), pady=(12, 8))
        estilo_label(c, "Sempre o único disponível (índice 1)", fraco=True).grid(
            row=9, column=1, sticky="w", padx=(0, 16), pady=(12, 8))

        # Botão ir para itens
        estilo_btn(c, "Ir para Itens  →", lambda: self.nb.select(1)).grid(
            row=10, column=0, columnspan=2, pady=(8, 16))

    # ── aba 2: itens ───────────────────────────
    def _aba_itens(self):
        frame = tk.Frame(self.nb, bg=COR["fundo"])
        self.nb.add(frame, text="  Itens  ")

        # formulário de novo item
        form = card(frame)
        form.pack(fill="x", padx=0, pady=(8, 4))
        form.columnconfigure(1, weight=1)

        # Espécie
        self.v_esp = tk.StringVar()
        combo_esp = estilo_combo(form, ESPECIES, self.v_esp, width=20)
        combo_esp.bind("<KeyRelease>", lambda e: self._filtrar_combo(
            combo_esp, ESPECIES, self.v_esp.get()))
        linha_form(form, "Espécie", combo_esp, 0)

        # PA
        self.v_pa = tk.StringVar()
        linha_form(form, "PA do Produto", estilo_entry(form, self.v_pa, width=12), 1)
        estilo_label(form, "Código numérico, ex: 0203", fraco=True).grid(
            row=2, column=1, sticky="w", padx=(0, 16))

        # Quantidade
        self.v_qtd = tk.StringVar()
        linha_form(form, "Quantidade (kg)", estilo_entry(form, self.v_qtd, width=12), 3)

        # Valor solicitado
        self.v_val = tk.StringVar()
        linha_form(form, "Valor Solicitado", estilo_entry(form, self.v_val, width=12), 4)
        estilo_label(form, "O sistema decide se anota na obs. ou altera", fraco=True).grid(
            row=5, column=1, sticky="w", padx=(0, 16))

        estilo_btn(form, "+ Adicionar Item", self._adicionar_item_lista,
                   cor=COR["verde"]).grid(row=6, column=0, columnspan=2, pady=(8, 12))

        # tabela de itens
        tbl_frame = card(frame)
        tbl_frame.pack(fill="both", expand=True, padx=0, pady=4)

        cols = ("Espécie", "PA", "Qtd (kg)", "Valor")
        style = ttk.Style()
        style.configure("Dark.Treeview",
            background=COR["fundo"], foreground=COR["texto"],
            fieldbackground=COR["fundo"], borderwidth=0,
            font=FONTE_INPUT, rowheight=26)
        style.configure("Dark.Treeview.Heading",
            background=COR["borda"], foreground=COR["acento"],
            font=FONTE_LABEL, borderwidth=0, relief="flat")
        style.map("Dark.Treeview",
            background=[("selected", COR["acento2"])],
            foreground=[("selected", COR["texto"])],
        )

        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                  style="Dark.Treeview", height=7)
        for col, w in zip(cols, (140, 70, 90, 90)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 4))

        # botões da tabela
        btn_row = tk.Frame(frame, bg=COR["fundo"])
        btn_row.pack(fill="x", pady=(4, 8))
        estilo_btn(btn_row, "✕  Remover Selecionado",
                   self._remover_item, cor="#374151").pack(side="left", padx=4)
        estilo_btn(btn_row, "▶  Executar Pedido",
                   self._executar, cor=COR["acento"]).pack(side="right", padx=4)

    # ── aba 3: log ─────────────────────────────
    def _aba_log(self):
        frame = tk.Frame(self.nb, bg=COR["fundo"])
        self.nb.add(frame, text="  Log  ")

        self.log_text = tk.Text(
            frame, font=FONTE_LOG,
            bg=COR["fundo"], fg=COR["texto"],
            insertbackground=COR["acento"],
            relief="flat", state="disabled",
            wrap="word"
        )
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        self.log_text.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 4))

        # tags de cor no log
        self.log_text.tag_config("ok",      foreground=COR["verde"])
        self.log_text.tag_config("erro",    foreground=COR["vermelho"])
        self.log_text.tag_config("aviso",   foreground=COR["amarelo"])
        self.log_text.tag_config("info",    foreground=COR["acento"])
        self.log_text.tag_config("normal",  foreground=COR["texto"])

    # ── helpers ────────────────────────────────

    def log(self, msg, tipo="normal"):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n", tipo)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _filtrar_combo(self, combo, lista, digitado):
        filtrado = [x for x in lista if digitado.lower() in x.lower()]
        combo["values"] = filtrado if filtrado else lista

    def _adicionar_item_lista(self):
        esp = self.v_esp.get().strip().lower()
        pa  = self.v_pa.get().strip().zfill(4)
        qtd = self.v_qtd.get().strip().replace(",", ".")
        val = self.v_val.get().strip().replace(",", ".")

        if not esp:
            messagebox.showwarning("Campo vazio", "Preencha a Espécie.")
            return
        if not pa or pa == "0000":
            messagebox.showwarning("Campo vazio", "Preencha o PA do produto.")
            return
        try:
            qtd_f = float(qtd)
        except ValueError:
            messagebox.showerror("Valor inválido", "Quantidade deve ser um número.")
            return
        try:
            val_f = float(val)
        except ValueError:
            messagebox.showerror("Valor inválido", "Valor deve ser um número.")
            return

        item = {"especie": esp, "pa": pa, "quantidade": qtd_f, "valor": val_f}
        self.itens.append(item)
        self.tree.insert("", "end", values=(
            esp.capitalize(), pa,
            f"{qtd_f:.3f}".rstrip("0").rstrip("."),
            f"R$ {val_f:.2f}"
        ))

        # limpa campos para próximo item
        self.v_esp.set("")
        self.v_pa.set("")
        self.v_qtd.set("")
        self.v_val.set("")

    def _remover_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        self.tree.delete(sel[0])
        self.itens.pop(idx)

    def _validar_pedido(self):
        erros = []
        if not self.v_ordem.get().strip():
            erros.append("Ordem de Compra")
        if not self.v_data.get().strip():
            erros.append("Data de Entrega")
        if not self.v_cliente.get().strip():
            erros.append("Cliente")
        if not self.v_pagto.get().strip():
            erros.append("Cond. Pagamento")
        if not self.itens:
            erros.append("Nenhum item adicionado")
        return erros

    def _montar_pedido(self):
        return {
            "ordem":          self.v_ordem.get().strip(),
            "data":           self.v_data.get().strip(),
            "cliente":        self.v_cliente.get().strip().lower(),
            "pagamento":      self.v_pagto.get().strip().lower(),
            "observacao":     self.txt_obs.get("1.0", "end").strip(),
            "empresa_index":  1,
            "vendedor_index": 1,
        }

    def _executar(self):
        erros = self._validar_pedido()
        if erros:
            messagebox.showerror("Campos obrigatórios",
                "Preencha os seguintes campos antes de continuar:\n\n• " +
                "\n• ".join(erros))
            return

        confirma = messagebox.askyesno(
            "Confirmar execução",
            f"Pedido para:  {self.v_cliente.get()}\n"
            f"Data:         {self.v_data.get()}\n"
            f"Itens:        {len(self.itens)}\n\n"
            "Iniciar automação?"
        )
        if not confirma:
            return

        self.nb.select(2)   # vai para aba Log
        self.log("═" * 50, "info")
        self.log("  INICIANDO AUTOMAÇÃO", "info")
        self.log("═" * 50, "info")

        # roda em thread para não travar a janela
        t = threading.Thread(target=self._rodar_automacao, daemon=True)
        t.start()

    def _rodar_automacao(self):
        import importlib, sys, os

        # importa o módulo de automação do mesmo diretório
        pasta = os.path.dirname(os.path.abspath(__file__))
        if pasta not in sys.path:
            sys.path.insert(0, pasta)

        try:
            import main as bot
        except Exception as ex:
            self.log(f"[ERRO] Não foi possível importar main.py: {ex}", "erro")
            return

        dados = self._montar_pedido()

        # injeta os dados no módulo
        bot.pedido.update(dados)

        # redireciona print para o log da interface
        import builtins
        _print_orig = builtins.print
        def _print_gui(*args, **kw):
            msg = " ".join(str(a) for a in args)
            if "[OK]" in msg:
                tag = "ok"
            elif "[ERRO]" in msg or "[PULADO]" in msg:
                tag = "erro"
            elif "[AVISO]" in msg or "INFERIOR" in msg:
                tag = "aviso"
            else:
                tag = "normal"
            self.after(0, lambda m=msg, t=tag: self.log(m, t))
            _print_orig(*args, **kw)
        builtins.print = _print_gui

        try:
            bot.driver.get("http://45.228.140.38:8082/WebSGEP/")
            bot.fazer_login()
            bot.abrir_novo_pedido()
            bot.selecionar_empresa()
            bot.preencher_data()
            bot.preencher_ordem()
            bot.selecionar_cliente()
            bot.selecionar_vendedor()
            bot.selecionar_pagamento()
            bot.preencher_observacao_inicial()
            bot.gravar_pedido()
            bot.abrir_aba_itens()

            for item in self.itens:
                bot.adicionar_item(
                    item["especie"], item["pa"],
                    item["quantidade"], item["valor"]
                )

            self.after(0, lambda: self.log("\n✔  PEDIDO CONCLUÍDO COM SUCESSO!", "ok"))
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", "Pedido enviado com sucesso!\nVerifique o sistema."))

        except Exception as ex:
            self.after(0, lambda e=str(ex): self.log(f"[ERRO FATAL] {e}", "erro"))
            self.after(0, lambda: messagebox.showerror(
                "Erro na automação", str(ex)))
        finally:
            builtins.print = _print_orig


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()