# ─────────────────────────────────────────────
#  pages/pdf.py — download automático do PDF
# ─────────────────────────────────────────────

import time
import os
import glob

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import utils.driver as _drv
from utils.waits import aguardar, limpar_e_digitar, clicar_js, fechar_popup_swal
from config import SEL

PASTA_PDF = r"D:\Documento\#Pedidos"

SEL_FILTRO = {
    "aba_filtro": "#filtro",
    "data_ini":   "#DtaIni",
    "btn_pesq":   "#btnPesquisar",
    "tabela":     "#example",
}


def _d():
    return _drv.driver


def _nome_esperado(codigo, cliente, data_pedido):
    """Nome do arquivo que vamos renomear para o padrão correto."""
    cliente_limpo = (cliente.upper()
                     .replace(" ", "_")
                     .replace("/", "-")[:30])
    data_limpa = data_pedido.replace("/", "-")
    return f"PEDIDO_{codigo}_{cliente_limpo}_{data_limpa}.pdf"


def _verificar_pedido_na_tabela(codigo):
    try:
        WebDriverWait(_d(), 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SEL_FILTRO["tabela"]))
        )
        links = _d().find_elements(
            By.CSS_SELECTOR, f'{SEL_FILTRO["tabela"]} tbody td a'
        )
        for link in links:
            onclick = link.get_attribute("onclick") or ""
            if str(codigo) in onclick or str(codigo) == link.text.strip():
                return True
        return False
    except Exception:
        return False


def _aguardar_download(timeout=30):
    """
    Aguarda um novo PDF aparecer na pasta de downloads.
    Retorna o caminho do arquivo baixado, ou None se timeout.
    """
    # Registra os PDFs que já existiam antes
    antes = set(glob.glob(os.path.join(PASTA_PDF, "*.pdf")))

    fim = time.time() + timeout
    while time.time() < fim:
        agora = set(glob.glob(os.path.join(PASTA_PDF, "*.pdf")))
        novos = agora - antes

        # Ignora arquivos .crdownload (ainda baixando)
        novos_completos = [
            f for f in novos
            if not f.endswith(".crdownload") and os.path.getsize(f) > 0
        ]

        if novos_completos:
            return novos_completos[0]
        time.sleep(0.5)

    return None


def baixar_pdf(codigo, cliente, data_pedido):
    print(f"\n[PDF] Iniciando download — Pedido #{codigo}")

    d = _d()

    # 1. Ir para o Filtro
    clicar_js(SEL["btn_pedidos"])
    time.sleep(0.5)
    try:
        aguardar(SEL_FILTRO["aba_filtro"]).click()
    except Exception:
        d.find_element(By.CSS_SELECTOR, SEL_FILTRO["aba_filtro"]).click()
    time.sleep(0.8)

    # 2. Preencher data e pesquisar
    limpar_e_digitar(SEL_FILTRO["data_ini"], data_pedido)
    time.sleep(0.3)
    clicar_js(SEL_FILTRO["btn_pesq"])
    try:
        WebDriverWait(d, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'{SEL_FILTRO["tabela"]} tbody tr'))
        )
    except Exception:
        pass
    time.sleep(1)

    # 3. Verificar pedido na lista
    if not _verificar_pedido_na_tabela(codigo):
        print(f"[PDF] [AVISO] Pedido #{codigo} não encontrado na lista.")
        return False
    print(f"[PDF] Pedido #{codigo} encontrado.")

    # 4. Chamar ImprimirPedido via JS
    # O Chrome vai baixar direto na pasta configurada, sem perguntar
    print(f"[PDF] Chamando impressão com valor...")
    d.execute_script(f"ImprimirPedido({codigo}, 'ComValor')")
    fechar_popup_swal(timeout=3)

    # 5. Aguardar o arquivo aparecer na pasta
    print(f"[PDF] Aguardando download...")
    arquivo_baixado = _aguardar_download(timeout=30)

    if not arquivo_baixado:
        print(f"[PDF] [AVISO] Download não detectado em {PASTA_PDF}.")
        return False

    # 6. Renomear para o padrão correto
    nome_final  = _nome_esperado(codigo, cliente, data_pedido)
    caminho_final = os.path.join(PASTA_PDF, nome_final)

    try:
        # Se já existir um arquivo com esse nome, remove antes
        if os.path.exists(caminho_final):
            os.remove(caminho_final)
        os.rename(arquivo_baixado, caminho_final)
        print(f"[PDF] [OK] Arquivo salvo: {nome_final}")
        return True
    except Exception as ex:
        # Renomear falhou mas o arquivo existe com o nome original
        nome_orig = os.path.basename(arquivo_baixado)
        print(f"[PDF] [OK] Arquivo baixado (nome original): {nome_orig}")
        print(f"[PDF]       (não foi possível renomear: {ex})")
        return True