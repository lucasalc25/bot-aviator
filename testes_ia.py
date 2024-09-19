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
chrome_options.add_argument("user-data-dir=c:\\Users\\Lucas\\AppData\\Local\\Google\\Chrome\\UserData")

 
# Inicializa o navegador
servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico, options=chrome_options)

# Acessa a página desejada
url = "https://www.claro.bet/slots/all/95/spribe/37591-806666-aviator?mode=fun"
driver.get(url)

# Aguarde a página carregar completamente
time.sleep(13)

preparar_pagina(driver)

saldo_parcial = capturar_saldo(driver)
stop_win = saldo_parcial + saldo_parcial * 0.2
stop_loss = saldo_parcial - saldo_parcial * 0.2
lista_numeros_anterior = []
valor_aposta = saldo_parcial * 0.02
multiplicador = 1.5
num_apostas = 0
aposta_preparada = False   

# Simulação contínua de geração de números e previsão
while True:
    nova_lista_numeros = capturar_numeros(driver)

     # Verifica se as duas listas têm ao menos um elemento antes de acessar o índice 0
    if nova_lista_numeros and len(nova_lista_numeros) > 0 and len(lista_numeros_anterior) > 0:
        if not aposta_preparada:
            threading.Thread(target=preparar_aposta, args=(valor_aposta, multiplicador)).start()
            aposta_preparada = True
        
        if nova_lista_numeros[0] != lista_numeros_anterior[0]:
            print("Mudança detectada!")

            # Treina o modelo
            treinamento_concluido, modelo, scaler = treinar_modelo(nova_lista_numeros, multiplicador)
            
            if treinamento_concluido:
                while True:
                    nova_lista_numeros = capturar_numeros(driver)
                    
                    if float(nova_lista_numeros[0]) != float(lista_numeros_anterior[0]):
                        # Faz a previsão
                        previsao = fazer_previsao(modelo, scaler, nova_lista_numeros[0])
                        
                        if previsao:
                            print(f"Grande probabilidade do próximo número ser maior ou igual a 1.5")
                            saldo_parcial = capturar_saldo(driver)
                            num_apostas += 1
                            # Executa a aposta
                            apostar(num_apostas, valor_aposta, multiplicador)

                            saldo_final = capturar_saldo(driver)
                            
                            resultado = str(input("Você ganhou a aposta? (S/N)")).lower()

                            verificar_aposta(driver, resultado, num_apostas, valor_aposta, multiplicador, saldo_final, stop_win, stop_loss)
                        else:
                            print(f"Baixa probabilidade do próximo número ser maior ou igual a 1.5")

                    # Aposta processada, desbloqueia a próxima aposta
                    aposta_preparada = False
                    lista_numeros_anterior = nova_lista_numeros  # Atualiza a lista de números após a aposta
                  
    else:
        lista_numeros_anterior = nova_lista_numeros  # Atualiza a lista de números após a aposta
        print("Nenhuma mudança nos números capturados, esperando nova rodada...")
        time.sleep(1)