#############################
#BIBLIOTECAS
#############################

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

#############################
#CONFIG
#############################

clientes_especiais = {
    "formosa_d": {"busca": "formosa", "value": "328"},
    "formosa_cn": {"busca": "formosa", "value": "327"},
    "formosa_agm": {"busca": "formosa", "value": "332"},
    "formosa_cu": {"busca": "formosa", "value": "329"},
    "formosa_g": {"busca": "formosa", "value": "9180"},
    "rest_cortizu": {"busca": "cortizu", "value": "5860"},
    "mc_solano": {"busca": "mc solano", "value": "9411"},
    "trs": {"busca": "trs de souza", "value": "9410"},
    "s alb": {"busca": "s albuquerque", "value": "409"},
    "fas": {"busca": "fas queiroz", "value": "595"},
    "ds": {"busca": "ds muller", "value": "330"},
}

cliente_normal = {
    "compespa","assembleia","jo","lucelia","lider",
    "cambuci","r3x","shopping","kenko","amazonia","dumar"
}

# HTML
usuario_input = "#USUEMAIL"
senha_input = "#USUSENHA"
botao_login_selector = ".sartec-btn-login"
btn_verde_pedidos = "#atalhos"
aba_pedidos = "#pedido"
drop_empresa = "#EMPCODIGO"
data_input = "#PEDDTPREVENTREGA"
ordem_compra_input = "#PEDORDEMCOMPRA"
clientes_input = "#CLICODIGO"
vendedor_select = "#VENCODIGO"
cond_pagto_select = "#CPACODIGO"
observacao_input = "#PEDOBS"
especie_input = "#ESPCODIGO"
produto_input = "#PROCODIGO"
und_input = "#IPEUNIMEDIDA"
qtd_input = "#IPEQTDE"
valor_input = "#IPEVLUNITARIO"

salvar_pedido_btn = "#btnGravarPedido"
salvar_item_btn = "#btnGravar"

#############################
#DADOS
#############################

usuario = "Americo.Lima"
senha = "amlima1947"

pedido = {
    "cliente": "compespa",
    "data": "09/04/2026",
    "ordem": "0",
    "pagamento": "30",
    "observacao": "ENTREGAR PELA MANHÃ",
    "empresa_index": 1,
    "vendedor_index": 1,
    "valor_minimo": 10
}

#############################
#FUNÇÕES
#############################

def esperar(driver):
    return WebDriverWait(driver, 10)

def esperar_elemento(driver, valor):
    return esperar(driver).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, valor))
    )

def escolher_cliente(nome):
    if nome in clientes_especiais:
        return clientes_especiais[nome]
    elif nome in cliente_normal:
        return {"busca": nome, "value": None}
    else:
        raise ValueError(f"Cliente '{nome}' não encontrado")

def fazer_login():
    esperar_elemento(driver, usuario_input).send_keys(usuario)
    esperar_elemento(driver, senha_input).send_keys(senha)
    esperar_elemento(driver, botao_login_selector).click()

def selecionar_empresa():
    select = Select(esperar_elemento(driver, drop_empresa))
    esperar(driver).until(lambda d: len(select.options) > 1)
    select.select_by_index(pedido["empresa_index"])

def digitar_data():
    campo = esperar_elemento(driver, data_input)
    campo.send_keys(Keys.CONTROL + "a", Keys.DELETE, pedido["data"])

def digitar_ordem():
    esperar_elemento(driver, ordem_compra_input).send_keys(pedido["ordem"])

def digitar_cliente():
    dados = escolher_cliente(pedido["cliente"])
    campo = esperar_elemento(driver, clientes_input)

    if dados["value"]:
        Select(campo).select_by_value(str(dados["value"]))
        return

    campo.send_keys(Keys.CONTROL + "a", Keys.DELETE, dados["busca"])
    time.sleep(1)
    campo.send_keys(Keys.ENTER)

def selecionar_vendedor():
    select_element = esperar_elemento(driver, vendedor_select)
    select = Select(select_element)

    esperar(driver).until(lambda d: len(select.options) > 1)

    total = len(select.options)
    index = pedido["vendedor_index"]

    if index >= total:
        raise Exception(f"Index {index} inválido. Só existem {total} opções.")

    select.select_by_index(index)

def selecionar_pagamento():
    select = Select(esperar_elemento(driver, cond_pagto_select))
    entrada = pedido["pagamento"].lower().strip()

    for opcao in select.options:
        texto = opcao.text.lower().strip()
        if entrada == texto:
            opcao.click()
            return

    for opcao in select.options:
        texto = opcao.text.lower().strip()
        if texto.startswith(entrada):
            opcao.click()
            return

    for opcao in select.options:
        texto = opcao.text.lower()
        if entrada in texto:
            opcao.click()
            return

    raise Exception("Pagamento não encontrado")

def escrever_observacao():
    campo = esperar_elemento(driver, observacao_input)
    atual = campo.get_attribute("value")

    if atual:
        campo.send_keys(Keys.END, Keys.ENTER)

    campo.send_keys(pedido["observacao"])

def salvar_pedido():
    esperar_elemento(driver, salvar_pedido_btn).click()

def verificar_erro_produto():
    try:
        erro = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal-text"))
        )
        if "não encontrado" in erro.text.lower():
            print(f"[ERRO] {erro.text}")
            driver.find_element(By.CSS_SELECTOR, ".swal-button--confirm").click()
            return True
    except:
        return False

def adicionar_item(especie, produto_pa, quantidade, valor_venda):
    # 1. Preenche espécie e produto
    esperar_elemento(driver, especie_input).send_keys(especie, Keys.ENTER)
    time.sleep(1)
    campo_produto = esperar_elemento(driver, produto_input)
    campo_produto.send_keys(produto_pa, Keys.ENTER)
    time.sleep(1)

    # 2. Captura o valor que o sistema sugere automaticamente
    valor_sistema_str = esperar_elemento(driver, valor_input).get_attribute("value")
    # Converte para número (ajustando vírgula se necessário)
    valor_sistema = float(valor_sistema_str.replace(',', '.'))

    # 3. Regra de Ouro: Se o valor do pai for menor que o do sistema
    if valor_venda < valor_sistema:
        print(f"Preço menor detectado para {produto_pa}. Indo para Observações...")
        # Clica na aba Pedidos para voltar
        driver.find_element(By.CSS_SELECTOR, aba_pedidos).click()
        
        # Adiciona a anotação do PA na observação
        campo_obs = esperar_elemento(driver, observacao_input)
        texto_atual = campo_obs.get_attribute("value")
        nova_linha = f"PA {produto_pa} {valor_venda}"
        
        if texto_atual:
            campo_obs.send_keys(Keys.END, " / " + nova_linha)
        else:
            campo_obs.send_keys(nova_linha)
            
        # Grava o pedido novamente para salvar a observação (conforme o fluxo do sistema)
        driver.find_element(By.CSS_SELECTOR, salvar_pedido_btn).click()
        
        # Volta para a aba de Itens para continuar
        driver.find_element(By.CSS_SELECTOR, "#itenselecionado").click() # Ajustar se o ID for outro
    
    # 4. Continua o preenchimento do item
    esperar_elemento(driver, und_input).send_keys("KG")
    esperar_elemento(driver, qtd_input).send_keys(str(quantidade))
    # No valor, se for menor, o sistema exige que usemos o valor dele (já que o desconto vai na obs)
    final_valor = valor_venda if valor_venda >= valor_sistema else valor_sistema
    esperar_elemento(driver, valor_input).send_keys(Keys.CONTROL+"a", Keys.DELETE, str(final_valor))
    
    # 5. Salva o item
    driver.find_element(By.CSS_SELECTOR, salvar_item_btn).click()
    
#############################
#EXECUÇÃO
#############################

driver.get("http://45.228.140.38:8082/WebSGEP/")

fazer_login()
esperar_elemento(driver, btn_verde_pedidos).click()
esperar_elemento(driver, aba_pedidos).click()

selecionar_empresa()
digitar_data()
digitar_ordem()
digitar_cliente()
selecionar_vendedor()
selecionar_pagamento()
escrever_observacao()

salvar_pedido()

# 🔥 AGORA VOCÊ PODE ESCOLHER:
# automático OU manual

# automático:
# adicionar_item("pescada", "0001", 10, 9.5)

# manual (você usa no sistema enquanto o código roda)

input("Pressione ENTER para fechar")