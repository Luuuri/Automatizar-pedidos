from selenium.webdriver.common.by import By

# LOGIN

class Login:
    def __init__(self, driver):
        self.driver = driver

def fazer_login(self, usuario, senha):
    ## Usuário
    campo_usuario = self.driver.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#USUEMAIL"))
    )
    campo_usuario.send_keys("Americo.Lima")

    ## Senha
    campo_senha = driver.find_element(By.CSS_SELECTOR, "#USUSENHA")
    campo_senha.send_keys("amlima1947")

    ## Botão Login
    botao_login = driver.find_element(By.CSS_SELECTOR, ".sartec-btn-login")
    botao_login.click()