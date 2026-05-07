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
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--allow-running-insecure-content")

    # ── Configura download automático sem perguntar ──────────────────
    prefs = {
        "download.default_directory": PASTA_PDF,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        
        # Desativa completamente o Safe Browsing
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "safebrowsing.disable_extension_thumbnail_detection": True,
        
        # Permite downloads inseguros
        "profile.default_content_setting_values.notifications": 2,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        
        # PDFs abrem diretamente sem visualizador
        "plugins.always_open_pdf_externally": True,
        
        # Permite downloads sem URL segura
        "profile.default_content_setting_values.unsandboxed_https_responses": 1,
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