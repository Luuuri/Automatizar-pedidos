# ─────────────────────────────────────────────
#  pages/pdf.py — download automático do PDF
# ─────────────────────────────────────────────

import time
import os
import glob
import shutil
from datetime import date

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import utils.driver as _drv
from utils.driver import PASTA_PDF
from utils.waits import aguardar, limpar_e_digitar, clicar_js, fechar_popup_swal
from config import SEL

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


def _configurar_download_cdp(d):
    """Usa Chrome DevTools Protocol para forçar o download automático sem perguntar."""
    try:
        d.execute_cdp_cmd("Browser.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": PASTA_PDF,
            "eventsEnabled": True,
        })
        print(f"[PDF] CDP Browser download configurado: {PASTA_PDF}")
        return True
    except Exception:
        pass
    try:
        d.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": PASTA_PDF,
        })
        print(f"[PDF] CDP Page download configurado: {PASTA_PDF}")
        return True
    except Exception as ex:
        print(f"[PDF] CDP fallback: {ex}")
        return False


def _garantir_pasta():
    """Garante que a pasta de downloads existe e limpa .crdownload antigos."""
    os.makedirs(PASTA_PDF, exist_ok=True)
    # Remove .crdownload com mais de 5 minutos (arquivos travados)
    for f in glob.glob(os.path.join(PASTA_PDF, "*.crdownload")):
        try:
            idade_min = (time.time() - os.path.getmtime(f)) / 60
            if idade_min > 5:
                os.remove(f)
                print(f"[PDF] Limpo .crdownload antigo: {os.path.basename(f)}")
        except Exception:
            pass


def _snapshot_pdfs():
    """Retorna dict {caminho: tamanho} dos PDFs na pasta."""
    return {f: os.path.getsize(f) for f in glob.glob(os.path.join(PASTA_PDF, "*.pdf"))}


def _aguardar_download(timeout=90, snapshot_ini=None):
    """
    Aguarda um novo PDF aparecer na pasta de downloads.
    Detecta tanto arquivos NOVOS quanto SOBRESCRITOS (mesmo nome, tamanho mudou).
    Se snapshot_ini for fornecido, usa como estado ANTES (tirado antes de ImprimirPedido).
    """
    _garantir_pasta()

    # Usa o snapshot fornecido ou tira um novo
    if snapshot_ini is not None:
        antes_pdfs, antes_cr = snapshot_ini
    else:
        antes_pdfs = _snapshot_pdfs()
        antes_cr   = set(glob.glob(os.path.join(PASTA_PDF, "*.crdownload")))

    fim = time.time() + timeout
    while time.time() < fim:
        # Pega .crdownload atuais e filtra apenas os NOVOS
        cr_atual = set(glob.glob(os.path.join(PASTA_PDF, "*.crdownload")))
        cr_novos = cr_atual - antes_cr

        if cr_novos:
            time.sleep(1)
            continue

        # Checa PDFs: novos OU modificados (sobrescritos)
        agora_pdfs = _snapshot_pdfs()

        # Arquivos que NÃO existiam antes e têm tamanho > 0
        nomes_novos = set(agora_pdfs.keys()) - set(antes_pdfs.keys())
        novos = [f for f in nomes_novos if agora_pdfs[f] > 0]

        # Arquivos que JÁ existiam mas mudaram de tamanho (sobrescritos)
        modificados = []
        for caminho, tam_atual in agora_pdfs.items():
            tam_antes = antes_pdfs.get(caminho, -1)
            if tam_atual > 0 and tam_atual != tam_antes:
                modificados.append(caminho)

        candidatos = novos + modificados
        if candidatos:
            return max(candidatos, key=os.path.getmtime)

        # Também checa a pasta padrão do Chrome
        pasta_chrome = os.path.join(os.path.expanduser("~"), "Downloads")
        if pasta_chrome.lower() != PASTA_PDF.lower():
            cr_chrome_novos = set(glob.glob(os.path.join(pasta_chrome, "*.crdownload"))) - antes_cr
            pdfs_chrome = [
                f for f in glob.glob(os.path.join(pasta_chrome, "*.pdf"))
                if os.path.getsize(f) > 0
            ]
            if not cr_chrome_novos and pdfs_chrome:
                origem = sorted(pdfs_chrome, key=os.path.getmtime)[-1]
                destino = os.path.join(PASTA_PDF, os.path.basename(origem))
                try:
                    shutil.move(origem, destino)
                    print(f"[PDF] Arquivo movido da pasta Downloads para {PASTA_PDF}")
                    return destino
                except Exception:
                    return origem

        time.sleep(0.5)

    return None


def baixar_pdf(codigo, cliente, data_pedido):
    print(f"\n[PDF] Iniciando download — Pedido #{codigo}")

    d = _d()
    _garantir_pasta()

    # Configura via CDP para forçar download automático
    _configurar_download_cdp(d)

    # 1. Ir para o Filtro
    clicar_js(SEL["btn_pedidos"])
    time.sleep(0.5)
    try:
        aguardar(SEL_FILTRO["aba_filtro"]).click()
    except Exception:
        d.find_element(By.CSS_SELECTOR, SEL_FILTRO["aba_filtro"]).click()
    time.sleep(0.8)

    # 2. Preencher data de HOJE e pesquisar
    data_hoje = date.today().strftime("%d/%m/%Y")
    limpar_e_digitar(SEL_FILTRO["data_ini"], data_hoje)
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
    print(f"[PDF] Chamando impressão com valor...")
    janela_principal = d.current_window_handle

    # Tira snapshot ANTES de iniciar o download (o download é muito rápido)
    snapshot_antes = (_snapshot_pdfs(),
                      set(glob.glob(os.path.join(PASTA_PDF, "*.crdownload"))))

    try:
        d.execute_script(f"ImprimirPedido({codigo}, 'ComValor')")
    except Exception as ex:
        print(f"[PDF] [ERRO] Falha ao chamar impressão: {ex}")
        return False

    # Aguarda o download iniciar
    time.sleep(3)

    # Trata possíveis popups SweetAlert
    fechar_popup_swal(timeout=3)

    # Se uma nova janela/aba abriu, volta para a principal
    try:
        handles = d.window_handles
        if len(handles) > 1:
            for h in handles:
                if h != janela_principal:
                    try:
                        d.switch_to.window(h)
                        time.sleep(1)
                        fechar_popup_swal(timeout=2)
                    except Exception:
                        pass
            if janela_principal in d.window_handles:
                d.switch_to.window(janela_principal)
            else:
                d.switch_to.window(list(d.window_handles)[0])
    except Exception:
        try:
            d.switch_to.window(janela_principal)
        except Exception:
            pass

    time.sleep(1)

    # 5. Aguardar o arquivo aparecer na pasta
    print(f"[PDF] Aguardando download...")
    arquivo_baixado = _aguardar_download(timeout=90, snapshot_ini=snapshot_antes)

    if not arquivo_baixado:
        print(f"[PDF] [AVISO] Download não detectado em {PASTA_PDF}.")
        try:
            novos_cr = [f for f in os.listdir(PASTA_PDF) if f.endswith('.crdownload')]
            novos_pdf = [f for f in os.listdir(PASTA_PDF) if f.endswith('.pdf')]
            if novos_cr:
                print(f"[PDF] [DEBUG] .crdownload ainda ativos: {novos_cr}")
            elif novos_pdf:
                print(f"[PDF] [DEBUG] {len(novos_pdf)} PDFs na pasta (nenhum novo detectado).")
            else:
                print(f"[PDF] [DEBUG] Pasta vazia.")
        except Exception as e:
            print(f"[PDF] [DEBUG] Erro ao listar pasta: {e}")
        return False

    # 6. Renomear para o padrão correto
    nome_final  = _nome_esperado(codigo, cliente, data_pedido)
    caminho_final = os.path.join(PASTA_PDF, nome_final)

    try:
        if os.path.exists(caminho_final):
            os.remove(caminho_final)
        os.rename(arquivo_baixado, caminho_final)
        print(f"[PDF] [OK] Arquivo salvo: {nome_final}")
        return True
    except Exception as ex:
        nome_orig = os.path.basename(arquivo_baixado)
        print(f"[PDF] [OK] Arquivo baixado (nome original): {nome_orig}")
        print(f"[PDF]       (não foi possível renomear: {ex})")
        return True
