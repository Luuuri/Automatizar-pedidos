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
    3. Aguarda opções filtrarem
    4. Clica na opção desejada
    """
    d = _d()

    # Abre o dropdown
    btn = WebDriverWait(d, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'button[data-id="{data_id}"]'))
    )
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
        busca.clear()
        busca.send_keys(texto_busca)
        # Aguarda as opções filtrarem após a busca
        time.sleep(0.8)
    except Exception:
        pass  # sem campo de busca — continua

    # Aguarda pelo menos uma opção estar disponível
    alvo = texto_opcao.lower() if texto_opcao else None
    tentativas = 3
    for _ in range(tentativas):
        opcoes = d.find_elements(
            By.CSS_SELECTOR,
            ".bootstrap-select.open ul.dropdown-menu.inner li:not(.disabled) a span.text, "
            ".bootstrap-select.show ul.dropdown-menu.inner li:not(.disabled) a span.text"
        )
        if opcoes:
            break
        time.sleep(0.5)

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
    aguardar(SEL["btn_pedidos"]).click()
    time.sleep(0.5)
    aguardar(SEL["aba_pedidos"]).click()
    time.sleep(0.5)
    print("[OK] Aba Pedidos aberta")

def selecionar_empresa():
    esperar().until(
        lambda d: len(Select(d.find_element("css selector", SEL["empresa"])).options) > 1
    )
    Select(aguardar(SEL["empresa"])).select_by_index(pedido["empresa_index"])
    print("[OK] Empresa selecionada")

def _desabilitar_tab_botoes_data():
    """Remove botões 'Hoje', 'Amanhã', 'Seg' da navegação por TAB."""
    d = _d()
    d.execute_script("""
        document.querySelectorAll('button, a, input[type=button], input[type=submit]').forEach(el => {
            var txt = (el.textContent || el.value || '').trim().toLowerCase();
            if (txt === 'hoje' || txt === 'amanhã' || txt === 'amanha' || txt === 'seg' || txt === 'segunda') {
                el.setAttribute('tabindex', '-1');
            }
        });
    """)

def preencher_data():
    limpar_e_digitar(SEL["data_entrega"], pedido["data"])
    print(f"[OK] Data de entrega: {pedido['data']}")

def preencher_ordem():
    limpar_e_digitar(SEL["ordem_compra"], pedido["ordem"])
    print(f"[OK] Ordem de compra: {pedido['ordem']}")

def selecionar_cliente():
    dados = _escolher_cliente(pedido["cliente"])
    # Espera o <select> estar carregado COM opções (não só visível)
    WebDriverWait(_d(), 15).until(
        lambda d: len(Select(d.find_element(By.CSS_SELECTOR, SEL["cliente"])).options) > 1
    )
    time.sleep(0.5)
    campo = aguardar(SEL["cliente"])

    if dados["value"]:
        # Cliente especial — seleciona pelo value do <option>
        Select(campo).select_by_value(str(dados["value"]))
    else:
        # Cliente normal — digita o nome e aguarda o autocomplete
        campo.click()
        time.sleep(0.3)
        campo.send_keys(Keys.CONTROL + "a")
        campo.send_keys(Keys.DELETE)
        campo.send_keys(dados["busca"])
        # Aguarda as opções do autocomplete aparecerem
        time.sleep(1.5)
        # Tenta selecionar a primeira opção que aparece no dropdown
        opcoes = campo.find_elements(By.XPATH, "ancestor::select//option")
        if len(opcoes) > 1:
            # Se o select tem opções filtradas, seleciona a primeira que contém o texto
            for op in opcoes:
                if dados["busca"].lower() in op.text.lower():
                    Select(campo).select_by_visible_text(op.text)
                    time.sleep(0.3)
                    break
            else:
                # Fallback: envia ENTER
                campo.send_keys(Keys.ENTER)
        else:
            campo.send_keys(Keys.ENTER)
        time.sleep(0.8)

    # Verifica se o cliente foi realmente selecionado
    if dados["value"]:
        selecionado = Select(campo).first_selected_option.get_attribute("value")
        if selecionado != str(dados["value"]):
            print(f"[AVISO] Cliente não selecionado corretamente, tentando novamente...")
            time.sleep(1)
            Select(campo).select_by_value(str(dados["value"]))
            time.sleep(0.5)
    print(f"[OK] Cliente: {pedido['cliente']}")

def selecionar_vendedor():
    Select(aguardar(SEL["vendedor"])).select_by_index(pedido["vendedor_index"])
    print("[OK] Vendedor selecionado")

def _normalizar(texto):
    """Remove 'dias', espaços extras e acentos para comparação robusta."""
    t = texto.lower().strip()
    t = t.replace("dias", "").strip()
    for antigo, novo in [("á","a"),("à","a"),("â","a"),("ã","a"),
                         ("é","e"),("ê","e"),("í","i"),("ó","o"),
                         ("ô","o"),("õ","o"),("ú","u"),("ü","u"),
                         ("ç","c")]:
        t = t.replace(antigo, novo)
    t = " ".join(t.split())
    return t

def selecionar_pagamento():
    select = Select(aguardar(SEL["cond_pagto"]))
    entrada = _normalizar(pedido["pagamento"])

    # Pula opções inativas ou de erro
    def _valida(texto):
        t = texto.lower()
        return "inativo" not in t and "erro" not in t

    # ── 1. Match exato (já normalizado) ──
    for opcao in select.options:
        if not _valida(opcao.text):
            continue
        if _normalizar(opcao.text) == entrada:
            opcao.click()
            print(f"[OK] Pagamento: {opcao.text.strip()}")
            return

    # ── 2. Token match — cada token individualmente ──
    # Evita "21/28" casar "21/28/35 DIAS" no contains
    for opcao in select.options:
        if not _valida(opcao.text):
            continue
        tokens = _normalizar(opcao.text).split()
        for token in tokens:
            if token == entrada:
                opcao.click()
                print(f"[OK] Pagamento: {opcao.text.strip()} (token)")
                return

    # ── 3. Contém (ex: "30/60" → "30/60 DIAS") ──
    for opcao in select.options:
        if not _valida(opcao.text):
            continue
        if entrada in _normalizar(opcao.text):
            opcao.click()
            print(f"[OK] Pagamento: {opcao.text.strip()}")
            return

    # ── 4. Fallback por starts_with ──
    for opcao in select.options:
        if not _valida(opcao.text):
            continue
        if _normalizar(opcao.text).startswith(entrada):
            opcao.click()
            print(f"[OK] Pagamento: {opcao.text.strip()} (aproximado)")
            return

    raise Exception(f"Condição de pagamento '{pedido['pagamento']}' não encontrada.")


def iniciar_driver():
    """Wrapper público para iniciar o Chrome."""
    _drv.iniciar()


def encerrar_driver():
    """Wrapper público para encerrar o Chrome."""
    _drv.encerrar()


def cancelar_pedido(codigo):
    """
    Vai para o Filtro, pesquisa o pedido pelo código e cancela.
    Equivale a clicar em GravarStatusPedido(codigo, '9') via JavaScript.
    """
    from config import URL_BASE
    from datetime import date as _date

    print(f"[CANCELAR] Buscando pedido #{codigo}...")
    _drv.iniciar()

    try:
        _d().get(URL_BASE)
    except Exception:
        _drv.encerrar()
        _drv.iniciar()
        _d().get(URL_BASE)
    time.sleep(1)

    clicar_js(SEL["btn_pedidos"])
    time.sleep(0.5)

    try:
        aguardar("#filtro").click()
    except Exception:
        _d().find_element(By.CSS_SELECTOR, "#filtro").click()
    time.sleep(1)

    try:
        campo_cod = _d().find_element(By.CSS_SELECTOR, "#PEDCODIGO")
        campo_cod.clear()
        campo_cod.send_keys(str(codigo))
    except Exception:
        hoje = _date.today()
        inicio_mes = hoje.replace(day=1).strftime("%d/%m/%Y")
        data_hoje = hoje.strftime("%d/%m/%Y")
        limpar_e_digitar("#DtaIni", inicio_mes)
        try:
            campo_fim = _d().find_element(By.CSS_SELECTOR, "#DtaFim")
            campo_fim.clear()
            campo_fim.send_keys(data_hoje)
        except Exception:
            pass

    time.sleep(0.3)
    clicar_js("#btnPesquisar")

    try:
        WebDriverWait(_d(), 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#example tbody tr"))
        )
    except Exception:
        print(f"[CANCELAR] [ERRO] Nenhum resultado para pedido #{codigo}.")
        return False
    time.sleep(1)

    _d().execute_script(f"GravarStatusPedido({codigo}, '9')")
    time.sleep(1.5)

    texto = fechar_popup_swal(timeout=8)
    if texto:
        print(f"[CANCELAR] [OK] #{codigo} — {texto}")
    else:
        print(f"[CANCELAR] [OK] #{codigo} cancelado.")
    return True


def editar_pedido_sistema(codigo):
    """
    Vai para o Filtro, pesquisa o pedido e abre para edição no sistema.
    Navega até o pedido e clica em Editar, deixando o Chrome aberto para
    o usuário fazer alterações manuais.
    """
    from config import URL_BASE
    from datetime import date as _date

    print(f"[EDITAR] Buscando pedido #{codigo}...")
    _drv.iniciar()

    try:
        _d().get(URL_BASE)
    except Exception:
        _drv.encerrar()
        _drv.iniciar()
        _d().get(URL_BASE)
    time.sleep(1)

    clicar_js(SEL["btn_pedidos"])
    time.sleep(0.5)

    try:
        aguardar("#filtro").click()
    except Exception:
        _d().find_element(By.CSS_SELECTOR, "#filtro").click()
    time.sleep(1)

    try:
        campo_cod = _d().find_element(By.CSS_SELECTOR, "#PEDCODIGO")
        campo_cod.clear()
        campo_cod.send_keys(str(codigo))
    except Exception:
        hoje = _date.today()
        inicio_mes = hoje.replace(day=1).strftime("%d/%m/%Y")
        data_hoje = hoje.strftime("%d/%m/%Y")
        limpar_e_digitar("#DtaIni", inicio_mes)
        try:
            campo_fim = _d().find_element(By.CSS_SELECTOR, "#DtaFim")
            campo_fim.clear()
            campo_fim.send_keys(data_hoje)
        except Exception:
            pass

    time.sleep(0.3)
    clicar_js("#btnPesquisar")

    try:
        WebDriverWait(_d(), 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#example tbody tr"))
        )
    except Exception:
        print(f"[EDITAR] [ERRO] Nenhum resultado para pedido #{codigo}.")
        return False
    time.sleep(1)

    # Tenta clicar no link de edição do pedido na tabela
    try:
        links = _d().find_elements(By.CSS_SELECTOR, "#example tbody td a")
        for link in links:
            onclick = link.get_attribute("onclick") or ""
            if str(codigo) in onclick:
                link.click()
                print(f"[EDITAR] [OK] Pedido #{codigo} aberto para edição.")
                return True
    except Exception as ex:
        print(f"[EDITAR] [ERRO] Falha ao abrir pedido: {ex}")
        return False

    print(f"[EDITAR] [AVISO] Não foi localizar link de edição para #{codigo}.")
    return False

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
        print("[AVISO] Popup não apareceu — tentando aguardar gravação...")

    # Aguarda o código do pedido aparecer no campo #PEDCODIGO
    codigo = None
    for _ in range(10):  # tenta por até ~5 segundos
        codigo = _ler_codigo()
        if codigo:
            break
        time.sleep(0.5)

    if codigo:
        print(f"[OK] Código do pedido capturado: {codigo}")
    else:
        # Se não capturou, força reabertura da aba Pedidos e tenta ler novamente
        print("[AVISO] Código não capturado, reabrindo aba Pedidos...")
        clicar_js(SEL["aba_pedidos"])
        time.sleep(1)
        codigo = _ler_codigo()
        if codigo:
            print(f"[OK] Código recuperado: {codigo}")
        else:
            print("[ERRO] Não foi possível capturar o código do pedido.")
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
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    print(f"[CONFERIR] Buscando pedido #{codigo}...")

    # Garante que o driver está ativo
    _drv.iniciar()

    # Garante que está na página certa
    try:
        _d().get(URL_BASE)
    except Exception:
        _drv.encerrar()
        _drv.iniciar()
        _d().get(URL_BASE)
    time.sleep(1)

    clicar_js(SEL["btn_pedidos"])
    time.sleep(0.5)

    try:
        aguardar("#filtro").click()
    except Exception:
        _d().find_element(By.CSS_SELECTOR, "#filtro").click()
    time.sleep(1)

    # Tenta buscar pelo código do pedido
    try:
        campo_cod = _d().find_element(By.CSS_SELECTOR, "#PEDCODIGO")
        campo_cod.clear()
        campo_cod.send_keys(str(codigo))
    except Exception:
        # Fallback: busca por data — intervalo amplo
        hoje = _date.today()
        inicio_mes = hoje.replace(day=1).strftime("%d/%m/%Y")
        data_hoje = hoje.strftime("%d/%m/%Y")
        limpar_e_digitar("#DtaIni", inicio_mes)
        try:
            campo_fim = _d().find_element(By.CSS_SELECTOR, "#DtaFim")
            campo_fim.clear()
            campo_fim.send_keys(data_hoje)
        except Exception:
            pass

    time.sleep(0.3)
    clicar_js("#btnPesquisar")

    try:
        WebDriverWait(_d(), 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#example tbody tr"))
        )
    except Exception:
        print(f"[CONFERIR] [ERRO] Nenhum resultado encontrado para pedido #{codigo}.")
        return False
    time.sleep(1)

    # Chama GravarStatusPedido via JS — equivale ao botão Conferir
    _d().execute_script(f"GravarStatusPedido({codigo}, '2')")
    time.sleep(1.5)

    texto = fechar_popup_swal(timeout=8)
    if texto:
        print(f"[CONFERIR] [OK] #{codigo} — {texto}")
    else:
        print(f"[CONFERIR] [OK] #{codigo} conferido.")

# ── execução completa ─────────────────────────

def executar_pedido(dados_pedido, itens):
    global _ultima_especie, _und_medida_preenchida
    _ultima_especie        = None
    _und_medida_preenchida = False

    pedido.update(dados_pedido)

    # Cria o Chrome aqui, não na importação
    _drv.iniciar()

    from config import URL_BASE
    _d().get(URL_BASE)

    fazer_login()
    abrir_novo_pedido()
    time.sleep(1)
    _desabilitar_tab_botoes_data()
    selecionar_empresa()
    preencher_data()
    preencher_ordem()
    selecionar_cliente()
    selecionar_vendedor()
    selecionar_pagamento()
    preencher_observacao_inicial()

    codigo = gravar_pedido()
    if not codigo:
        raise Exception("Pedido não foi gravado — código não gerado. "
                        "Verifique se a data é válida e se o cliente foi selecionado corretamente.")

    abrir_aba_itens()

    for item in itens:
        adicionar_item(item["especie"], item["pa"], item["quantidade"], item["valor"])

    print("\n=== PEDIDO CONCLUÍDO! ===")
    return codigo