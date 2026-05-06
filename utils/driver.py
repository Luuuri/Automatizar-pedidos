# ─────────────────────────────────────────────
#  utils/driver.py
# ─────────────────────────────────────────────

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

PASTA_PDF = r"D:\Documento\#Pedidos"

driver = None

def iniciar():
    global driver
    if driver is not None:
        try:
            driver.current_url
            return driver
        except Exception:
            driver = None
    
    opts = webdriver.ChromeOptions()
    opts.add_argument("--force-device-scale-factor=0.8")
    opts.add_argument("--start-maximized")
    opts.add_argument("--new-window")

    # ── Configura download automático sem perguntar ──────────────────
    # Define a pasta de destino e desativa o aviso de download perigoso
    prefs = {
        # Pasta onde os arquivos vão ser salvos automaticamente
        "download.default_directory": PASTA_PDF,

        # Não pergunta onde salvar — baixa direto na pasta acima
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,

        # Desativa o aviso de "arquivo perigoso" para sites HTTP
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,

        # Permite PDFs serem baixados em vez de abrir no visualizador
        "plugins.always_open_pdf_externally": True,
    }
    opts.add_experimental_option("prefs", prefs)

    # Suprime logs desnecessários do Chrome
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    return driver

def encerrar():
    global driver
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
        driver = None