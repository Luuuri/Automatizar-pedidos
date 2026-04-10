# ─────────────────────────────────────────────
#  utils/waits.py — helpers de espera e clique
# ─────────────────────────────────────────────

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import utils.driver as _drv   # importa o módulo, não o objeto
import time


def _d():
    """Retorna o driver atual (criado sob demanda)."""
    return _drv.driver


def esperar(segundos=10):
    return WebDriverWait(_d(), segundos)

def aguardar(seletor, segundos=10):
    return WebDriverWait(_d(), segundos).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, seletor))
    )

def limpar_e_digitar(seletor, texto):
    campo = aguardar(seletor)
    campo.click()
    time.sleep(0.1)
    campo.send_keys(Keys.CONTROL + "a")
    campo.send_keys(Keys.DELETE)
    campo.send_keys(str(texto))
    return campo

def clicar_js(seletor):
    d = _d()
    elemento = aguardar(seletor)
    d.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
    time.sleep(0.3)
    d.execute_script("arguments[0].click();", elemento)

def fechar_popup_swal(timeout=10):
    from config import SEL
    d = _d()
    try:
        WebDriverWait(d, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, SEL["erro_swal"]))
        )
        texto = d.find_element(By.CSS_SELECTOR, SEL["erro_swal"]).text.strip()
        d.find_element(By.CSS_SELECTOR, SEL["btn_confirmar"]).click()
        WebDriverWait(d, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, SEL["erro_swal"]))
        )
        return texto
    except Exception:
        return None