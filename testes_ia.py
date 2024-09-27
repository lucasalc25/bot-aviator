import time
import joblib
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import seaborn as sns
import matplotlib.pyplot as plt
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

# Inicializa o modelo RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)

# Carrega o modelo e dados previamente salvos (se existirem)
if os.path.exists('modelo_treinado.pkl') and os.path.exists('dados_X.npy') and os.path.exists('dados_y.npy'):
    model = joblib.load('modelo_treinado.pkl')
    X = np.load('dados_X.npy')
    y = np.load('dados_y.npy')
    print("Modelo e dados carregados com sucesso.")
else:
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    X = np.empty((0, 1))  # Inicializa X vazio
    y = np.array([])  # Inicializa y vazio
    print("Nenhum modelo ou dados anteriores encontrados, iniciando um novo treinamento.")

preparar_pagina(driver)

saldo = capturar_saldo(driver)
stop_win = saldo + saldo * 0.2
stop_loss = saldo - saldo * 0.2
lista_numeros_anterior = []
tentativas = 0
accuracy = 0
acertos = 0
erros = 0
alta_prob = False
baixa_prob = False

# Loop até que a acurácia seja superior a 85%
while True: 
    nova_lista_numeros = capturar_numeros(driver)

    # Verifica se as duas listas têm ao menos um elemento antes de acessar o índice 0
    if nova_lista_numeros and len(nova_lista_numeros) > 0 and len(lista_numeros_anterior) > 0:
        if nova_lista_numeros[0] != lista_numeros_anterior[0]:
            print(nova_lista_numeros)

            novos_X, novos_y = preparar_dados(nova_lista_numeros)

            # Verifica a dimensionalidade de novos_X
            print(f"Dimensões de novos_X: {novos_X.shape}")

            # Se X estiver vazio, inicializa com o número correto de colunas
            if X.size == 0:
                X = np.empty((0, novos_X.shape[1]))  # Inicializa com o mesmo número de colunas que novos_X
                print(f"X inicializado com {X.shape[1]} colunas.")

            # Verifica se as dimensões batem antes de empilhar
            if X.shape[1] == novos_X.shape[1]:
                X = np.vstack((X, novos_X))  # Adiciona novos dados de entrada
                y = np.concatenate((y, novos_y))  # Adiciona novos rótulos
                print(f"Modelo atualizado com {len(X)} amostras.")
            else:
                print(f"Erro: O número de colunas de X ({X.shape[1]}) não bate com novos_X ({novos_X.shape[1]})")

            # Treinamento incremental (aprendizado online)
            model.fit(X, y)  # O RandomForest não suporta partial_fit, então re-treinamos com todos os dados

            # Salva o modelo e os dados atualizados
            joblib.dump(model, 'modelo_treinado.pkl')
            np.save('dados_X.npy', X)
            np.save('dados_y.npy', y)

            print(f"Modelo atualizado com {len(X)} amostras.")

            # Divide os dados em treinamento (80%) e teste (20%)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Treina o modelo nos dados de treinamento
            model.fit(X_train, y_train)

            # Converte X_test para valores numéricos, caso contenha strings
            X_test = np.array(X_test).astype(float)

            # Faz previsões nos dados de teste
            y_pred = model.predict(X_test)

            # Calcula as métricas de avaliação
            acuracia = accuracy_score(y_test, y_pred)
            precisao = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)

            print(f"Acurácia: {acuracia * 100:.2f}%")
            print(f"Precisão: {precisao * 100:.2f}%")
            print(f"Recall: {recall * 100:.2f}%")
            print(f"F1-Score: {f1 * 100:.2f}%")

            scores = cross_val_score(model, X, y, cv=5)  # 5-fold cross-validation
            print("Acurácia média: ", scores.mean())

            if acuracia >= 0.80:
                print("A IA atingiu a acurácia desejada, começando as previsões em tempo real...")

                while True:
                    nova_lista_numeros = capturar_numeros(driver)
                   
                    if nova_lista_numeros and len(nova_lista_numeros) > 0 and len(lista_numeros_anterior) > 0:
                        if nova_lista_numeros[0] != lista_numeros_anterior[0]:
                            if verificar_predominancia(nova_lista_numeros) == True: # Verifica se as duas listas têm ao menos um elemento antes de acessar o índice 0
                                print(nova_lista_numeros)

                                if alta_prob == True:
                                    if float(nova_lista_numeros[0]) >= 2:
                                        acertos += 1
                                    else:
                                        erros += 1

                                print(f"\n{acertos} acertos até o momento")
                                print(f"{erros} erros até o momento\n")

                                media_movel = calcular_media_movel(nova_lista_numeros)
                                desvio_padrao = calcular_desvio_padrao(nova_lista_numeros)
                                diferencas = calcular_diferencas(nova_lista_numeros)
                                
                                # Cria a matriz X com quatro features: número atual, diferença entre números, desvio padrão e média móvel
                                X_real_time = np.array([[float(nova_lista_numeros[-1]), diferencas[-1], desvio_padrao[-1], media_movel[-1]]])

                                previsao = model.predict(X_real_time)[0]

                                if previsao == 1:
                                    print("Grande probabilidade de ser maior ou igual a 2.00x")
                                    alta_prob = True 
                                else: 
                                    print("Baixa probabilidade de ser maior ou igual a 2.00x")
                                    alta_prob = False
                            else:
                                time.sleep(600)
                    lista_numeros_anterior = nova_lista_numeros
            else:
                print("A IA ainda não atingiu a acurácia desejada. Aguardando para capturar novos dados...")                      

    lista_numeros_anterior = nova_lista_numeros

    # Se a lista anterior estiver vazia, atualiza com a nova lista para evitar a próxima comparação
    if not lista_numeros_anterior:
        lista_numeros_anterior = nova_lista_numeros
    


            

    