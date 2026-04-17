# ─────────────────────────────────────────────
#  pages/whatsapp.py — envio de PDF via WhatsApp Web
# ─────────────────────────────────────────────

import time
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import utils.driver as _drv

CONTATO   = "Pai Américo"
PASTA_PDF = r"D:\Documento\#Pedidos"
URL_WA    = "https://web.whatsapp.com"


def _d():
    return _drv.driver


def _aguardar_wa_carregar(timeout=60):
    """
    Aguarda o WhatsApp Web estar pronto.
    Aceita tanto a tela principal quanto a tela de QR code
    (nesse caso aguarda até o login ser feito).
    """
    print("[WA] Aguardando WhatsApp Web carregar...")
    d = _d()

    # Aguarda desaparecer o splash de carregamento
    WebDriverWait(d, timeout).until(
        lambda drv: drv.execute_script(
            "return document.readyState") == "complete"
    )
    time.sleep(2)

    # Se aparecer QR code, aguarda o usuário escanear (até timeout)
    fim = time.time() + timeout
    while time.time() < fim:
        # Sinal de que está logado: existe a caixa de pesquisa de conversa
        logado = d.find_elements(
            By.CSS_SELECTOR,
            '[data-testid="chat-list-search"], '
            '[aria-label="Caixa de texto de pesquisa"], '
            'div[contenteditable][data-tab="3"]'
        )
        if logado:
            print("[WA] Logado e pronto.")
            return
        time.sleep(1.5)

    raise Exception("WhatsApp Web não carregou dentro do tempo limite.")


def _buscar_contato(nome):
    """Abre a busca e clica no contato."""
    d = _d()

    # Clica na lupa / campo de busca — tenta vários seletores
    for sel in [
        '[data-testid="chat-list-search"]',
        '[aria-label="Caixa de texto de pesquisa"]',
        'div[contenteditable][data-tab="3"]',
        'div[role="textbox"]',
    ]:
        try:
            campo = WebDriverWait(d, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            campo.click()
            time.sleep(0.3)
            campo.send_keys(nome)
            break
        except Exception:
            continue
    else:
        raise Exception("Campo de busca do WhatsApp não encontrado.")

    time.sleep(1.5)

    # Clica no primeiro resultado que contenha o nome
    for sel in [
        f'span[title="{nome}"]',
        f'span[title*="{nome.split()[0]}"]',
        '[data-testid="cell-frame-title"]',
    ]:
        try:
            resultado = WebDriverWait(d, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            resultado.click()
            time.sleep(1)
            print(f"[WA] Conversa com '{nome}' aberta.")
            return
        except Exception:
            continue

    raise Exception(f"Contato '{nome}' não encontrado na busca do WhatsApp.")


def _anexar_e_enviar(caminho_pdf):
    """Anexa o PDF e envia."""
    d = _d()

    # Botão de clipe/anexo — tenta vários seletores
    for sel in [
        '[data-testid="attach-menu-plus"]',
        '[title="Anexar"]',
        'span[data-icon="attach-menu-plus"]',
        '[data-testid="clip"]',
        'button[aria-label="Anexar"]',
    ]:
        try:
            btn = WebDriverWait(d, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            d.execute_script("arguments[0].click();", btn)
            time.sleep(0.8)
            break
        except Exception:
            continue
    else:
        raise Exception("Botão de anexo não encontrado.")

    # Input de arquivo — fica oculto, envia o caminho diretamente
    for sel in [
        'input[type="file"][accept*="*"]',
        'input[type="file"]',
        '[data-testid="media-input"]',
    ]:
        try:
            inp = WebDriverWait(d, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            inp.send_keys(caminho_pdf)
            time.sleep(2)
            break
        except Exception:
            continue
    else:
        raise Exception("Input de arquivo não encontrado.")

    # Botão de enviar — aparece após selecionar o arquivo
    for sel in [
        '[data-testid="send"]',
        '[aria-label="Enviar"]',
        'span[data-icon="send"]',
        'button[aria-label="Enviar"]',
    ]:
        try:
            btn_env = WebDriverWait(d, 8).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            d.execute_script("arguments[0].click();", btn_env)
            time.sleep(1.5)
            print(f"[WA] PDF enviado: {os.path.basename(caminho_pdf)}")
            return
        except Exception:
            continue

    # Fallback: tenta Enter na caixa de texto da conversa
    try:
        caixa = d.find_element(By.CSS_SELECTOR,
            'div[contenteditable][data-tab="10"], '
            'div[contenteditable][data-tab="6"]')
        caixa.send_keys(Keys.ENTER)
        time.sleep(1.5)
        print(f"[WA] PDF enviado via Enter: {os.path.basename(caminho_pdf)}")
    except Exception:
        raise Exception("Botão de enviar não encontrado após anexar arquivo.")


def enviar_pdf(caminho_pdf):
    """
    Abre o WhatsApp Web numa nova aba do Chrome já aberto,
    busca o contato e envia o PDF.
    """
    d = _d()
    aba_original = d.current_window_handle

    # Abre nova aba com o WhatsApp Web
    d.execute_script(f"window.open('{URL_WA}', '_blank');")
    time.sleep(1)

    nova_aba = [h for h in d.window_handles if h != aba_original][-1]
    d.switch_to.window(nova_aba)

    try:
        _aguardar_wa_carregar(timeout=60)
        _buscar_contato(CONTATO)
        _anexar_e_enviar(caminho_pdf)
    finally:
        try:
            d.close()
        except Exception:
            pass
        try:
            d.switch_to.window(aba_original)
        except Exception:
            pass