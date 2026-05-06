# ─────────────────────────────────────────────
#  pages/pedidos.py — automação do fluxo de pedidos
# ─────────────────────────────────────────────

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import utils.driver as _drv
from utils.waits import aguardar, esperar, limpar_e_digitar, clicar_js, fechar_popup_swal
from config import SEL, LOGIN, CLIENTES_ESPECIAIS, CLIENTES_NORMAIS
import time

pedido = {
    "cliente":        "",
    "data":           "",
    "ordem":          "0",
    "pagamento":      "",
    "observacao":     "",
    "empresa_index":  1,
    "vendedor_index": 1,
}

def _d():
    return _drv.driver

# ── Bootstrap Select ──────────────────────────

def _bsselect_buscar_e_selecionar(data_id, texto_busca, texto_opcao=None):
    """
    Interage com dropdowns Bootstrap Select:
    1. Clica no botão para abrir
    2. Digita no campo de busca interno
    3. Clica na opção desejada
    """
    d = _d()

    # Abre o dropdown
    btn = d.find_element(By.CSS_SELECTOR, f'button[data-id="{data_id}"]')
    d.execute_script("arguments[0].click();", btn)
    time.sleep(0.5)

    # Campo de busca interno do bootstrap-select
    try:
        busca = WebDriverWait(d, 4).until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, ".bootstrap-select.open .bs-searchbox input, "
                                 ".bootstrap-select.show .bs-searchbox input"
            ))
        )
        busca.send_keys(texto_busca)
        time.sleep(0.6)
    except Exception:
        pass  # sem campo de busca — continua

    # Clica na opção correta
    alvo = texto_opcao.lower() if texto_opcao else None
    opcoes = d.find_elements(
        By.CSS_SELECTOR,
        ".bootstrap-select.open ul.dropdown-menu.inner li:not(.disabled) a span.text, "
        ".bootstrap-select.show ul.dropdown-menu.inner li:not(.disabled) a span.text"
    )

    for opcao in opcoes:
        texto = opcao.text.strip()
        if not texto:
            continue
        if alvo:
            if alvo in texto.lower():
                d.execute_script("arguments[0].click();", opcao)
                time.sleep(0.3)
                return texto
        else:
            d.execute_script("arguments[0].click();", opcao)
            time.sleep(0.3)
            return texto

    raise Exception(f"Opção '{texto_opcao or texto_busca}' não encontrada no bs-select [{data_id}]")

# ── helpers internos ──────────────────────────

def _escolher_cliente(nome):
    if nome in CLIENTES_ESPECIAIS:
        return CLIENTES_ESPECIAIS[nome]
    elif nome in CLIENTES_NORMAIS:
        return {"busca": nome, "value": None}
    else:
        raise ValueError(f"Cliente '{nome}' não cadastrado no config.py.")

def _anotar_preco_observacao(pa, valor):
    nota = f"PA {pa} {f'{valor:.2f}'.replace('.', ',')}"

    clicar_js(SEL["aba_pedidos"])
    time.sleep(0.8)

    campo = aguardar(SEL["observacao"])
    atual = campo.get_attribute("value").strip()
    if atual:
        campo.send_keys(Keys.END)
        campo.send_keys(" / ")
    campo.send_keys(nota)
    print(f"         [OBS] Anotado: {nota}")

    # Grava o pedido novamente para persistir a observação no sistema
    clicar_js(SEL["salvar_pedido"])
    fechar_popup_swal(timeout=10)
    print(f"         [OBS] Pedido regravado com observação.")

    clicar_js("#pedidoitem")
    time.sleep(0.8)

def _ler_codigo():
    time.sleep(0.5)
    try:
        campo = _d().find_element(By.CSS_SELECTOR, "#PEDCODIGO")
        valor = campo.get_attribute("value").strip()
        return valor if valor and valor != "0" else None
    except Exception:
        return None

# ── etapas do pedido ──────────────────────────

def fazer_login():
    aguardar(SEL["usuario"]).send_keys(LOGIN["usuario"])
    aguardar(SEL["senha"]).send_keys(LOGIN["senha"])
    aguardar(SEL["btn_login"]).click()
    print("[OK] Login realizado")

def abrir_novo_pedido():
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        btn = WebDriverWait(_d(), 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SEL["btn_pedidos"]))
        )
        btn.click()
        time.sleep(0.8)
    except Exception:
        print("[AVISO] Botão pedidos não encontrado, recarregando página...")
        from config import URL_BASE
        _d().get(URL_BASE)
        time.sleep(1)
        fazer_login()
        time.sleep(1)
        aguardar(SEL["btn_pedidos"]).click()
        time.sleep(0.8)
    
    try:
        aguardar(SEL["aba_pedidos"]).click()
    except Exception:
        _d().find_element("css selector", SEL["aba_pedidos"]).click()
    time.sleep(0.8)
    print("[OK] Aba Pedidos aberta")

def selecionar_empresa():
    esperar().until(
        lambda d: len(Select(d.find_element("css selector", SEL["empresa"])).options) > 1
    )
    Select(aguardar(SEL["empresa"])).select_by_index(pedido["empresa_index"])
    print("[OK] Empresa selecionada")

def preencher_data():
    limpar_e_digitar(SEL["data_entrega"], pedido["data"])
    print(f"[OK] Data de entrega: {pedido['data']}")

def preencher_ordem():
    limpar_e_digitar(SEL["ordem_compra"], pedido["ordem"])
    print(f"[OK] Ordem de compra: {pedido['ordem']}")

def selecionar_cliente():
    dados = _escolher_cliente(pedido["cliente"])
    campo = aguardar(SEL["cliente"])
    
    time.sleep(0.3)
    campo.click()
    time.sleep(0.3)
    campo.send_keys(Keys.CONTROL + "a", Keys.DELETE)
    time.sleep(0.2)
    
    if dados["value"]:
        try:
            Select(campo).select_by_value(str(dados["value"]))
        except Exception as e:
            print(f"[AVISO] Value {dados['value']} não encontrada, buscando pelo nome...")
            campo.send_keys(dados["busca"])
            time.sleep(1.5)
            campo.send_keys(Keys.ENTER)
    else:
        campo.send_keys(dados["busca"])
        time.sleep(1.5)
        campo.send_keys(Keys.ENTER)
    
    time.sleep(0.5)
    print(f"[OK] Cliente: {pedido['cliente']}")

def selecionar_vendedor():
    Select(aguardar(SEL["vendedor"])).select_by_index(pedido["vendedor_index"])
    print("[OK] Vendedor selecionado")

def selecionar_pagamento():
    entrada = pedido["pagamento"].lower().strip()
    
    select = Select(aguardar(SEL["cond_pagto"]))
    
    opcoes_disponiveis = [opcao.text.strip() for opcao in select.options if opcao.text.strip()]
    
    achou = False
    opcao_encontrada = ""
    
    for modo in ("exato", "inicia", "contem"):
        for opcao in select.options:
            texto = opcao.text.lower().strip()
            achou = (
                (modo == "exato"  and texto == entrada) or
                (modo == "inicia" and texto.startswith(entrada)) or
                (modo == "contem" and entrada in texto)
            )
            if achou:
                opcao.click()
                opcao_encontrada = opcao.text.strip()
                break
        if achou:
            break
    
    if not achou:
        opcoes_str = ", ".join(opcoes_disponiveis[:5])
        raise Exception(
            f"Condição de pagamento '{pedido['pagamento']}' não encontrada no sistema.\n\n"
            f"Opções disponíveis: {opcoes_str}...\n\n"
            f"Por favor, corrija na tela de edição."
        )
    
    print(f"[OK] Pagamento: {opcao_encontrada}")

def preencher_observacao_inicial():
    texto = pedido["observacao"].strip()
    if not texto:
        return
    campo = aguardar(SEL["observacao"])
    campo.click()
    campo.send_keys(texto)
    print(f"[OK] Observação: {texto}")

def gravar_pedido():
    clicar_js(SEL["salvar_pedido"])
    texto = fechar_popup_swal(timeout=10)
    if texto:
        print(f"[OK] Pedido gravado — {texto}")
    else:
        print("[AVISO] Popup não apareceu — continuando mesmo assim")
    # Após gravar o sistema fica na aba Pedidos com o código preenchido
    codigo = _ler_codigo()
    if codigo:
        print(f"[OK] Código do pedido capturado: {codigo}")
    else:
        print("[AVISO] Código não capturado.")
    return codigo

def abrir_aba_itens():
    # ID correto conforme HTML inspecionado: id="pedidoitem"
    clicar_js("#pedidoitem")
    time.sleep(1)
    print("[OK] Aba Itens Pedidos aberta\n")

def verificar_erro_produto():
    texto = fechar_popup_swal(timeout=2)
    if texto and "não encontrado" in texto.lower():
        print(f"[ERRO] {texto}")
        return True
    return False

def ler_valor_sistema():
    campo = aguardar(SEL["valor_unit"])
    texto = campo.get_attribute("value").strip().replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0

# ── adição de itens ───────────────────────────

_ultima_especie        = None
_und_medida_preenchida = False

def adicionar_item(especie, pa, quantidade, valor_pedido):
    global _ultima_especie, _und_medida_preenchida

    print(f"\n[ITEM] {especie.upper()} | PA {pa} | {quantidade} kg | R$ {valor_pedido:.2f}")

    # 1. Espécie — só muda se diferente do item anterior
    if especie.lower() != (_ultima_especie or "").lower():
        texto_opcao = "rosa" if "camar" in especie.lower() else None
        nome_sel = _bsselect_buscar_e_selecionar("ESPCODIGO", especie, texto_opcao)
        print(f"         Espécie: {nome_sel}")
        _ultima_especie = especie.lower()
        time.sleep(0.3)
    else:
        print(f"         Espécie mantida: {especie}")

    # 2. Produto (PA)
    nome_prod = _bsselect_buscar_e_selecionar("PROCODIGO", pa)
    print(f"         Produto: {nome_prod}")
    time.sleep(0.8)

    if verificar_erro_produto():
        print(f"[PULADO] PA {pa} não encontrado.")
        return

    # 3. Uni. Medida (uma vez por pedido)
    if not _und_medida_preenchida:
        limpar_e_digitar(SEL["und_medida"], "KG")
        _und_medida_preenchida = True
        print("         Uni. Medida: KG")

    # 4. Quantidade (sempre sobrescreve)
    limpar_e_digitar(SEL["quantidade"], str(quantidade).replace(".", ","))

    # 5. Valor
    valor_sistema = ler_valor_sistema()
    print(f"         Sistema: R$ {valor_sistema:.2f} | Pedido: R$ {valor_pedido:.2f}", end=" → ")

    if valor_pedido < valor_sistema:
        print("INFERIOR — anotando em Observações")
        _anotar_preco_observacao(pa, valor_pedido)

        # Clica em Limpar para resetar todos os campos do item —
        # só assim o sistema repopula o valor ao re-selecionar o produto.
        print("         Clicando em Limpar para resetar campos...")
        clicar_js("#btnLimpar")
        time.sleep(0.5)

        # Refaz o fluxo completo: espécie → PA → uni. medida → quantidade.
        print("         Refazendo seleção completa...")

        texto_opcao = "rosa" if "camar" in especie.lower() else None
        _bsselect_buscar_e_selecionar("ESPCODIGO", especie, texto_opcao)
        time.sleep(0.4)

        _bsselect_buscar_e_selecionar("PROCODIGO", pa)
        time.sleep(0.8)

        # Uni. medida pode ter sido limpa também
        limpar_e_digitar(SEL["und_medida"], "KG")

        limpar_e_digitar(SEL["quantidade"], str(quantidade).replace(".", ","))

        # Confirma que o valor foi restaurado pelo sistema
        valor_apos = ler_valor_sistema()
        if valor_apos == 0.0:
            print("         [AVISO] Valor ainda 0,00 após refazer seleção.")
            print("         Verifique este item manualmente no sistema.")
        else:
            print(f"         Valor restaurado: R$ {valor_apos:.2f} (obs. já anotada)")

    elif valor_pedido > valor_sistema:
        print("SUPERIOR — alterando valor")
        limpar_e_digitar(SEL["valor_unit"], f"{valor_pedido:.2f}".replace(".", ","))

    else:
        print("IGUAL — sem alteração")

    # 6. Gravar
    clicar_js(SEL["salvar_item"])
    texto = fechar_popup_swal(timeout=10)
    if texto and "sucesso" in texto.lower():
        print(f"         [OK] PA {pa} gravado — {texto}")
    elif texto:
        print(f"         [AVISO] PA {pa} — resposta: {texto}")
    else:
        print(f"         [AVISO] PA {pa} — popup não apareceu.")

    time.sleep(0.5)


def conferir_pedido(codigo):
    """
    Vai para o Filtro, pesquisa o pedido pelo código e clica em Conferir.
    Equivale a clicar em GravarStatusPedido(codigo, '2') via JavaScript.
    """
    from config import URL_BASE
    from datetime import date as _date

    print(f"[CONFERIR] Buscando pedido #{codigo}...")

    clicar_js(SEL["btn_pedidos"])
    time.sleep(0.5)

    try:
        aguardar("#filtro").click()
    except Exception:
        _d().find_element("css selector", "#filtro").click()
    time.sleep(0.8)

    # Preenche a data de hoje e pesquisa
    limpar_e_digitar("#DtaIni", _date.today().strftime("%d/%m/%Y"))
    time.sleep(0.3)
    clicar_js("#btnPesquisar")

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    WebDriverWait(_d(), 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#example tbody tr"))
    )
    time.sleep(1)

    # Chama GravarStatusPedido via JS — equivale ao botão Conferir
    _d().execute_script(f"GravarStatusPedido({codigo}, '2')")
    time.sleep(1.5)

    texto = fechar_popup_swal(timeout=8)
    if texto:
        print(f"[CONFERIR] [OK] #{codigo} — {texto}")
    else:
        print(f"[CONFERIR] [OK] #{codigo} conferido.")

def cancelar_pedido(codigo):
    from config import URL_BASE, LOGIN
    print(f"[CANCELAR] Cancelando pedido #{codigo}...")
    
    url_atual = _d().current_url
    
    if "login" in url_atual.lower() or "entrar" in url_atual.lower():
        print("[CANCELAR] Sessão expirada, fazendo login...")
        _d().get(URL_BASE)
        time.sleep(2)
        fazer_login()
        time.sleep(1)
    
    try:
        btn = aguardar(SEL["btn_pedidos"], segundos=5)
        btn.click()
        time.sleep(0.8)
    except Exception:
        _d().get(URL_BASE)
        time.sleep(1)
        fazer_login()
        time.sleep(1)
        aguardar(SEL["btn_pedidos"]).click()
        time.sleep(0.8)
    
    try:
        aguardar("#filtro").click()
    except Exception:
        _d().find_element("css selector", "#filtro").click()
    time.sleep(0.8)
    
    from datetime import date as _date
    limpar_e_digitar("#DtaIni", _date.today().strftime("%d/%m/%Y"))
    time.sleep(0.3)
    clicar_js("#btnPesquisar")
    
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    
    WebDriverWait(_d(), 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#example tbody tr"))
    )
    time.sleep(1)
    
    _d().execute_script(f"CancelarPedido({codigo})")
    time.sleep(2)
    
    texto = fechar_popup_swal(timeout=8)
    if texto:
        print(f"[CANCELAR] [OK] #{codigo} — {texto}")
    else:
        print(f"[CANCELAR] [OK] #{codigo} cancelado.")

def editar_pedido_sistema(codigo):
    from config import URL_BASE, LOGIN
    print(f"[EDITAR] Editando pedido #{codigo} no sistema...")
    
    url_atual = _d().current_url
    
    if "login" in url_atual.lower() or "entrar" in url_atual.lower():
        print("[EDITAR] Sessão expirada, fazendo login...")
        _d().get(URL_BASE)
        time.sleep(2)
        fazer_login()
        time.sleep(1)
    
    try:
        btn = aguardar(SEL["btn_pedidos"], segundos=5)
        btn.click()
        time.sleep(0.8)
    except Exception:
        _d().get(URL_BASE)
        time.sleep(1)
        fazer_login()
        time.sleep(1)
        aguardar(SEL["btn_pedidos"]).click()
        time.sleep(0.8)
    
    try:
        aguardar("#filtro").click()
    except Exception:
        _d().find_element("css selector", "#filtro").click()
    time.sleep(0.8)
    
    from datetime import date as _date
    limpar_e_digitar("#DtaIni", _date.today().strftime("%d/%m/%Y"))
    time.sleep(0.3)
    clicar_js("#btnPesquisar")
    
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    
    WebDriverWait(_d(), 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#example tbody tr"))
    )
    time.sleep(1)
    
    _d().execute_script(f"CarregaDados({codigo})")
    time.sleep(2)
    
    print(f"[EDITAR] [OK] Pedido #{codigo} aberto para edição no sistema")

def validar_condicao_pagamento(condicao):
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.by import By
    
    try:
        select = Select(_d().find_element(By.CSS_SELECTOR, SEL["cond_pagto"]))
        opcoes = [opt.text.strip().lower() for opt in select.options if opt.text.strip()]
        
        cond_lower = condicao.lower().strip()
        
        for opcao in opcoes:
            if cond_lower == opcao:
                return True
            if cond_lower in opcao:
                return True
            if opcao in cond_lower:
                return True
        
        return False
    except Exception:
        return True

# ── execução completa ─────────────────────────

def iniciar_driver():
    global _ultima_especie, _und_medida_preenchida
    _ultima_especie        = None
    _und_medida_preenchida = False
    _drv.iniciar()
    return _d()

def encerrar_driver():
    _drv.encerrar()

def executar_pedido(dados_pedido, itens):
    global _ultima_especie, _und_medida_preenchida
    _ultima_especie        = None
    _und_medida_preenchida = False

    pedido.update(dados_pedido)

    from config import URL_BASE
    driver_atual = _d()
    if driver_atual is None:
        _drv.iniciar()
    
    url = ""
    try:
        url = _d().current_url
    except Exception:
        pass
    
    precisa_login = "login" in url.lower() or "entrar" in url.lower() or not url
    
    if precisa_login:
        _d().get(URL_BASE)
        time.sleep(1.5)
        fazer_login()
        time.sleep(1)
        abrir_novo_pedido()
    elif "WebSGEP" not in url:
        _d().get(URL_BASE)
        fazer_login()
        abrir_novo_pedido()
    else:
        try:
            aguardar(SEL["btn_pedidos"], segundos=3).click()
            time.sleep(0.8)
            aguardar(SEL["aba_pedidos"]).click()
            time.sleep(0.8)
        except Exception:
            _d().get(URL_BASE)
            fazer_login()
            abrir_novo_pedido()
    
    selecionar_empresa()
    preencher_data()
    preencher_ordem()
    selecionar_cliente()
    selecionar_vendedor()
    selecionar_pagamento()
    preencher_observacao_inicial()

    codigo = gravar_pedido()

    abrir_aba_itens()

    for item in itens:
        adicionar_item(item["especie"], item["pa"], item["quantidade"], item["valor"])

    print("\n=== PEDIDO CONCLUÍDO! ===")
    return codigo