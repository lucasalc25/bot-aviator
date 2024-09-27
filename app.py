import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from funcoes import *

# Configurações do navegador
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
 
# Inicializa o navegador
servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico, options=chrome_options)

# Acessa a página desejada
url = "https://www.claro.bet/slots/all/240/spribe/37591-806666-aviator?mode=fun"
driver.get(url)

# Aguarde a página carregar completamente
time.sleep(10)

preparar_pagina(driver)

saldo = capturar_saldo(driver)
stop_win = saldo + saldo * 0.2
stop_loss = saldo - saldo * 0.2
lista_numeros_anterior = []
valor_aposta = saldo * 0.02
multiplicador = 1.5
num_apostas = 0
tentativas = 0
aposta_preparada = False 

# Simulação contínua de geração de números e previsão
while True:
    nova_lista_numeros = capturar_numeros(driver)
    
    # Verifica se as duas listas têm ao menos um elemento antes de acessar o índice 0
    if nova_lista_numeros and len(nova_lista_numeros) > 0 and len(lista_numeros_anterior) > 0:
        if nova_lista_numeros[0] != lista_numeros_anterior[0]:
            # Treina o modelo
            treinamento_concluido, modelo, scaler = treinar_modelo(nova_lista_numeros, multiplicador)
            print(nova_lista_numeros)
            
            if treinamento_concluido:
                while True:
                    nova_lista_numeros = capturar_numeros(driver)

                    # Verifica se as duas listas têm ao menos um elemento antes de acessar o índice 0
                    if nova_lista_numeros and len(nova_lista_numeros) > 0 and len(lista_numeros_anterior) > 0:
                        if not aposta_preparada:
                            preparar_aposta(valor_aposta, multiplicador)
                            aposta_preparada = True

                        if nova_lista_numeros[0] != lista_numeros_anterior[0]:
                            # Faz a previsão
                            previsao = fazer_previsao(modelo, scaler, nova_lista_numeros[0])
                            
                            if previsao:
                                print(f"Grande probabilidade do próximo número ser maior ou igual a", multiplicador)
                                num_apostas += 1
                                tentativas += 1
                                apostar(num_apostas, valor_aposta, multiplicador)

                                saldo_final = capturar_saldo(driver)
                                
                                resultado = str(input("Você ganhou a aposta? (S/N)")).lower()
                                
                                num_apostas, valor_aposta, multiplicador = verificar_aposta(driver, resultado, num_apostas, valor_aposta, multiplicador, saldo_final, stop_win, stop_loss)

                                if tentativas > 1:
                                    aposta_preparada = False

                            else:
                                print(f"Baixa probabilidade do próximo número ser maior ou igual a", multiplicador)

                        lista_numeros_anterior = nova_lista_numeros

    lista_numeros_anterior = nova_lista_numeros

    # Se a lista anterior estiver vazia, atualiza com a nova lista para evitar a próxima comparação
    if not lista_numeros_anterior:
        lista_numeros_anterior = nova_lista_numeros
    

    