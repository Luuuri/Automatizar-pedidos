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
    # Tenta Browser.setDownloadBehavior (mais confiável)
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

    # Fallback: Page.setDownloadBehavior
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


def _aceitar_download_barras(d):
    """
    Tenta fechar/aceitar possíveis barras de download do Chrome
    via atalhos de teclado e JavaScript.
    """
    try:
        # Envia Alt+Shift+A para aceitar downloads perigosos (atalho do Chrome)
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys
        ActionChains(d).send_keys(Keys.ALT + Keys.SHIFT + "a").perform()
        time.sleep(0.3)
    except Exception:
        pass

    # Tenta clicar em botões de confirmação via JS (caso estejam no DOM)
    try:
        d.execute_script("""
            document.querySelectorAll('#save-file, .download-button, [id*="keep"], [class*="keep"]').forEach(el => {
                if (el.offsetParent !== null) el.click();
            });
        """)
    except Exception:
        pass


def _garantir_pasta():
    """Garante que a pasta de downloads existe."""
    os.makedirs(PASTA_PDF, exist_ok=True)


def _aguardar_download(timeout=90):
    """
    Aguarda um novo PDF aparecer na pasta de downloads.
    Retorna o caminho do arquivo baixado, ou None se timeout.
    """
    _garantir_pasta()

    antes_pdfs = set(glob.glob(os.path.join(PASTA_PDF, "*.pdf")))
    cr_anteriores = set(glob.glob(os.path.join(PASTA_PDF, "*.crdownload")))

    fim = time.time() + timeout
    ultimo_tamanho = {}
    tentativas_stuck = 0

    while time.time() < fim:
        cr_atual = set(glob.glob(os.path.join(PASTA_PDF, "*.crdownload")))

        if cr_atual:
            # Verifica se o download está travado (tamanho não muda)
            for cr in cr_atual:
                try:
                    tam = os.path.getsize(cr)
                    if cr in ultimo_tamanho and ultimo_tamanho[cr] == tam:
                        tentativas_stuck += 1
                        if tentativas_stuck >= 6:  # ~6 segundos sem mudar
                            print(f"[PDF] [DEBUG] Download pode estar travado. Tentando aceitar...")
                            _aceitar_download_barras(_d())
                            tentativas_stuck = 0
                    else:
                        ultimo_tamanho[cr] = tam
                        tentativas_stuck = 0
                except Exception:
                    pass
            time.sleep(1)
            continue

        # Se havia .crdownload e agora não tem mais, o download terminou
        agora_pdfs = set(glob.glob(os.path.join(PASTA_PDF, "*.pdf")))
        novos = agora_pdfs - antes_pdfs

        novos_completos = [
            f for f in novos
            if os.path.getsize(f) > 0
        ]

        if novos_completos:
            return novos_completos[0]

        # Também checa a pasta padrão do Chrome
        pasta_chrome = os.path.join(os.path.expanduser("~"), "Downloads")
        if pasta_chrome.lower() != PASTA_PDF.lower():
            cr_chrome = glob.glob(os.path.join(pasta_chrome, "*.crdownload"))
            pdfs_chrome = [
                f for f in glob.glob(os.path.join(pasta_chrome, "*.pdf"))
                if os.path.getsize(f) > 0
            ]
            if not cr_chrome and pdfs_chrome:
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

    try:
        d.execute_script(f"ImprimirPedido({codigo}, 'ComValor')")
    except Exception as ex:
        print(f"[PDF] [ERRO] Falha ao chamar impressão: {ex}")
        return False

    # Aguarda o download iniciar
    time.sleep(3)

    # Trata possíveis popups SweetAlert
    fechar_popup_swal(timeout=3)

    # Tenta aceitar barra de download do Chrome
    _aceitar_download_barras(d)

    # Se uma nova janela/aba abriu (preview do PDF), volta para a principal
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
    arquivo_baixado = _aguardar_download(timeout=90)

    if not arquivo_baixado:
        print(f"[PDF] [AVISO] Download não detectado em {PASTA_PDF}.")
        try:
            conteudo = [f for f in os.listdir(PASTA_PDF) if f.endswith(('.pdf', '.crdownload'))]
            if conteudo:
                print(f"[PDF] [DEBUG] Arquivos na pasta: {conteudo[-5:]}")
            else:
                print(f"[PDF] [DEBUG] Pasta {PASTA_PDF} sem PDFs ou crdownloads.")
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
