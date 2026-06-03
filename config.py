# ─────────────────────────────────────────────
#  config.py — configurações centrais do projeto
#  Edite aqui: login, clientes, seletores HTML
# ─────────────────────────────────────────────

# ── Login ─────────────────────────────────────
LOGIN = {
    "usuario": "Americo.Lima",
    "senha":   "amlima1947",
}

# ── Clientes ──────────────────────────────────
# Clientes com múltiplos endereços ou nome diferente no sistema.
# Para descobrir o "value" correto: abra o site, inspecione o <select>
# de clientes e copie o atributo value do <option> desejado.
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
    "boteco":           {"busca": "boteco di",       "value": "9836"},
    "rede_mais_barato": {"busca": "mais barato",     "value": "7015"},
}

# Clientes que o sistema reconhece só pelo nome digitado.
CLIENTES_NORMAIS = {
    "compespa", "assembleia", "jo", "lucelia", "lider",
    "cambuci", "r3x", "shopping", "kenko", "amazonia", "dumar", "diniz",
}

# Lista unificada para a interface (dropdown)
TODOS_CLIENTES = sorted(list(CLIENTES_ESPECIAIS.keys()) + sorted(CLIENTES_NORMAIS))

# ── Condições de pagamento ────────────────────
PAGAMENTOS = [
    "a vista", "contrato", "7 dias", "14 dias", "21 dias", "21/28", "21/28/35","28 dias",
    "28/42", "30 dias", "30/60", "30/60/90", "45 dias", "60 dias", "28/35/42", "14/21/28"
]

# ── Espécies ──────────────────────────────────
ESPECIES = [
    "camarao", "dourada", "filhote", "jaraqui", "pirarucu",
    "pescada", "surubim", "tambaqui", "tucunare", "outros", "pargo"
]

# ── Seletores CSS do sistema SGEP ────────────
SEL = {
    "usuario":       "#USUEMAIL",
    "senha":         "#USUSENHA",
    "btn_login":     ".sartec-btn-login",
    "btn_pedidos":   "#atalhos",
    "aba_pedidos":   "#pedido",
    "aba_itens":     "#itensPedido",
    "empresa":       "#EMPCODIGO",
    "data_entrega":  "#PEDDTPREVENTREGA",
    "ordem_compra":  "#PEDORDEMCOMPRA",
    "cliente":       "#CLICODIGO",
    "vendedor":      "#VENCODIGO",
    "cond_pagto":    "#CPACODIGO",
    "observacao":    "#PEDOBS",
    "especie":       "#ESPCODIGO",
    "produto":       "#PROCODIGO",
    "und_medida":    "#IPEUNIMEDIDA",
    "quantidade":    "#IPEQTDE",
    "valor_unit":    "#IPEVLUNITARIO",
    "salvar_pedido": "#btnGravarPedido",
    "salvar_item":   "#btnGravar",
    "erro_swal":     ".swal-text",
    "btn_confirmar": ".swal-button--confirm",
}

# ── URL do sistema ────────────────────────────
URL_BASE = "http://45.228.140.38:8082/WebSGEP/"

# ── Padrões fixos (não mudam por pedido) ─────
EMPRESA_INDEX  = 1   # sempre a primeira opção real no dropdown
VENDEDOR_INDEX = 1   # normalmente só tem uma opção