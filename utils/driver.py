# ─────────────────────────────────────────────
#  utils/driver.py
# ─────────────────────────────────────────────

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

PASTA_PDF = r"D:\Documento\#Pedidos"

driver = None
_headless = False

def set_headless(mode):
    """Define se o Chrome será executado sem interface (headless)."""
    global _headless
    _headless = mode

def iniciar():
    global driver, _headless
    if driver is not None:
        # Verifica se a sessão ainda está viva
        try:
            _ = driver.title
            return driver
        except Exception:
            driver = None

    opts = webdriver.ChromeOptions()
    if _headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1920,1080")
    else:
        opts.add_argument("--force-device-scale-factor=0.8")
        opts.add_argument("--start-maximized")

    # ── Configura download automático sem perguntar ──────────────────
    prefs = {
        "download.default_directory": PASTA_PDF,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "safebrowsing.providing.enabled": False,
        "safebrowsing.enabled_v4": False,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.content_settings.exceptions.safe_browsing.*.setting": 1,
        "plugins.always_open_pdf_externally": True,
    }
    opts.add_experimental_option("prefs", prefs)
    opts.add_experimental_option("excludeSwitches", [
        "enable-logging",
        "enable-blink-features=AutomationControlled",
        "safebrowsing-disable-download-protection",
    ])
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--safebrowsing-disable-download-protection")
    opts.add_argument("--disable-features=DownloadBubble,DownloadBubbling")

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
