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

CONTATO   = "Pai Américo"          # nome exato como aparece no WhatsApp Web
PASTA_PDF = r"D:\Documento\#Pedidos"
URL_WA    = "https://web.whatsapp.com"


def _d():
    return _drv.driver


def _aguardar_wa_carregar(timeout=60):
    """
    Aguarda o WhatsApp Web carregar completamente.
    Na primeira vez, o usuário precisa escanear o QR code —
    o timeout de 60s dá tempo para isso.
    """
    print("[WA] Aguardando WhatsApp Web carregar...")
    WebDriverWait(_d(), timeout).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="3"], '
                              'div[role="textbox"]'))
    )
    print("[WA] WhatsApp Web carregado.")


def _buscar_contato(nome):
    """Abre a busca e encontra o contato pelo nome."""
    d = _d()

    # Clica no botão de nova conversa / busca
    btn_busca = WebDriverWait(d, 15).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            'div[contenteditable="true"][data-tab="3"], '
            'div[title="Caixa de texto de pesquisa"]'
        ))
    )
    btn_busca.click()
    time.sleep(0.5)
    btn_busca.send_keys(nome)
    time.sleep(1.5)

    # Clica no primeiro resultado
    resultado = WebDriverWait(d, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            f'//span[@title="{nome}"]'
        ))
    )
    resultado.click()
    time.sleep(1)
    print(f"[WA] Conversa com '{nome}' aberta.")


def _anexar_e_enviar(caminho_pdf):
    """Anexa o PDF e envia na conversa aberta."""
    d = _d()

    # Clica no botão de anexo (clipe)
    btn_anexo = WebDriverWait(d, 10).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            'div[title="Anexar"], '
            'button[aria-label="Anexar"], '
            'span[data-icon="attach-menu-plus"]'
        ))
    )
    btn_anexo.click()
    time.sleep(0.8)

    # Input de arquivo (fica oculto — envia o caminho diretamente)
    input_arquivo = WebDriverWait(d, 10).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            'input[type="file"][accept*="*"],'
            'input[type="file"]'
        ))
    )
    input_arquivo.send_keys(caminho_pdf)
    time.sleep(2)

    # Clica em Enviar
    btn_enviar = WebDriverWait(d, 10).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            'div[aria-label="Enviar"], '
            'span[data-icon="send"]'
        ))
    )
    btn_enviar.click()
    time.sleep(1.5)
    print(f"[WA] PDF enviado: {os.path.basename(caminho_pdf)}")


def enviar_pdf(caminho_pdf):
    """
    Ponto de entrada — abre o WhatsApp Web, busca o contato e envia o PDF.
    O Chrome já está aberto pela automação do pedido.
    """
    d = _d()
    aba_original = d.current_window_handle

    # Abre WhatsApp Web numa nova aba
    d.execute_script("window.open(arguments[0], '_blank');", URL_WA)
    time.sleep(1)

    # Muda para a nova aba
    nova_aba = [h for h in d.window_handles if h != aba_original][-1]
    d.switch_to.window(nova_aba)

    try:
        _aguardar_wa_carregar(timeout=60)
        _buscar_contato(CONTATO)
        _anexar_e_enviar(caminho_pdf)
    finally:
        # Fecha a aba do WhatsApp e volta para o SGEP
        try:
            d.close()
        except Exception:
            pass
        d.switch_to.window(aba_original)