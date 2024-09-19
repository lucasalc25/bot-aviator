import time
import pytesseract
import cv2
import pyautogui
from PIL import Image
import numpy as np
import numpy as np
from tensorflow import keras
from tensorflow.keras.layers import Dense # type: ignore
from keras import Sequential
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def preparar_pagina(driver):
    # Aumenta o zoom em 50%
    driver.execute_script(f"document.body.style.zoom='{1.50}'")
    time.sleep(1)
    # Clica em 'auto'
    pyautogui.click(976, 790)
    time.sleep(0.5)
    # Clica em 'auto saque'
    pyautogui.click(1000, 990)
    # Clica duplo no valor do auto saque
    pyautogui.doubleClick(1080, 990)
    # Digita o valor do multiplicador
    pyautogui.typewrite('1.5')
    # Clica para mostrar o histórico
    pyautogui.click(1826, 333)


def capturar_tela(driver, chave, x, y, xfinal, yfinal):
    # Adiciona uma pequena pausa
    time.sleep(3)

    # Captura a tela e salva como imagem
    screenshot_path = "screenshot.png"
    driver.save_screenshot(screenshot_path)

    # Abre a imagem completa
    image = Image.open(screenshot_path)
    
    # Recorta e salva a imagem para a área especificada
    image = image.crop((x, y, xfinal, yfinal))

    if chave == 1:
        image.save("screenshot_numeros.png")
        # Carregar a imagem da tela capturada
        return cv2.imread('screenshot_numeros.png')
    if chave == 2:
        image.save("screenshot_novo_numero.png")
        # Carregar a imagem da tela capturada
        return cv2.imread('screenshot_novo_numero.png')
    if chave == 3:
        image.save("screenshot_saldo.png")
        # Carregar a imagem da tela capturada
        return cv2.imread('screenshot_saldo.png')
    if chave == 4:
        image.save("screenshot_botao.png")
        # Carregar a imagem da tela capturada
        return cv2.imread('screenshot_botao.png')
    if chave == 5:
        image.save("screenshot_win.png")
        # Carregar a imagem da tela capturada
        return cv2.imread('screenshot_win.png')

def tratar_imagem(imagem):
    # Convert para escala de cinza
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Aumenta o contraste
    gray = cv2.convertScaleAbs(gray, alpha=2.5, beta=0)

    # Aplicar um filtro de nitidez para melhorar a definição dos números
    kernel = np.array([[0, -1, 0],
                    [-1,  5,-1],
                    [0, -1, 0]])
    sharp = cv2.filter2D(gray, -1, kernel)

    return sharp

def processar_string(texto):
    # Lista para armazenar os números processados
    numeros_processados = []
    
    # Remove espaços extras e separa os números pelos \n
    texto = texto.replace(" ", "").replace("\n", "")

    # Separa os números pelos pontos
    partes = texto.split('.')

    # Itera pelas partes, combinando-as para formar números válidos
    for i in range(len(partes) - 1):
        parte_inteira = partes[i]
        parte_decimal = partes[i + 1][:2]  # Pega os dois primeiros dígitos após o ponto
        
        # Adiciona '0' se a parte decimal tiver apenas um dígito
        if len(parte_decimal) == 1:
            parte_decimal += '0'
        elif len(parte_decimal) == 0:
            parte_decimal = '00'
        
        if i > 0:
            # Remove os dois primeiros dígitos da parte inteira, a partir do segundo número
            parte_inteira = parte_inteira[2:]
        
        # Verifica se a parte inteira tem mais que 4 dígitos, ou seja, é um número muito grande
        if len(parte_inteira) > 3:
            # Adiciona um ponto após o primeiro dígito e separa em dois números
            numero_1 = parte_inteira[:1] + '.' + parte_inteira[1:3]  # Primeiro número
            numero_2 = parte_inteira[3:] + '.' + parte_decimal  # Segundo número
            
            # Adiciona os dois números à lista processada
            numeros_processados.append(f"{float(numero_1):.2f}")
            numeros_processados.append(f"{float(numero_2):.2f}")
        else:
            # Cria o número formatado com dois dígitos após o ponto decimal
            numero_formatado = f"{parte_inteira}.{parte_decimal}"
            
            # Adiciona o número formatado com duas casas decimais
            numeros_processados.append(f"{float(numero_formatado):.2f}")

    return numeros_processados

# Função para capturar os números
def capturar_numeros(driver):
    imagem = capturar_tela(driver, 1, 595, 240, 1850, 325)

    sharp = tratar_imagem(imagem)

    # Configuração personalizada do Tesseract
    custom_config = r'--oem 3 --psm 6 outputbase digits'

    # Executar OCR na imagem com a configuração customizada
    texto = pytesseract.image_to_string(sharp, config=custom_config)

    try:
         # Lista para armazenar os números processados
        numeros_processados = processar_string(texto)
        
        return numeros_processados
     
    except ValueError as e:
        print("Erro ao processar string:", e)

# Função para preparar os dados
def preparar_dados(lista_numeros, multiplicador):
    # Converte lista de strings para floats
    lista_numeros = [float(num) for num in lista_numeros]
    
    # Normaliza os números
    scaler = MinMaxScaler()
    numeros_normalizados = scaler.fit_transform(np.array(lista_numeros).reshape(-1, 1))
    
    # Prepara os dados para o treinamento: X são os números atuais, y é o próximo número
    X, y = [], []
    for i in range(len(numeros_normalizados) - 1):
        X.append(numeros_normalizados[i])
        y.append(1 if lista_numeros[i + 1] >= multiplicador else 0)  # 1 se o próximo número >= multiplicador desejado, caso contrário 0
    
    return np.array(X), np.array(y), scaler

# Função para criar o modelo de rede neural
def criar_modelo(input_shape):
    model = Sequential([
        Dense(64, input_shape=(input_shape,), activation='relu'),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')  # Saída binária (0 ou 1)
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Função para treinar a IA
def treinar_modelo(lista_numeros, multiplicador):
    X, y, scaler = preparar_dados(lista_numeros, multiplicador)
    
    # Divide os dados em treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Cria o modelo
    model = criar_modelo(X_train.shape[1])
    
    # Treina o modelo
    model.fit(X_train, y_train, epochs=50, batch_size=4, verbose=1)
    
    # Avalia o modelo
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Acurácia no conjunto de teste: {accuracy * 100:.2f}%")
    
    # Verifica se a acurácia é suficiente
    if accuracy >= 0.9:
        print("A IA atingiu pelo menos 90% de precisão.")
        return True, model, scaler
    else:
        print("A IA não atingiu a precisão esperada.")
        return False, model, scaler


# Função para fazer previsões usando o modelo treinado
def fazer_previsao(model, scaler, novo_numero):
    print("Iniciando previsão...")
    # Normaliza o número de entrada
    numero_normalizado = scaler.transform(np.array([novo_numero]).reshape(-1, 1))
    
    # Faz a previsão
    previsao = model.predict(numero_normalizado)
    
    # Retorna o resultado
    return previsao[0][0] >= 0.5  # Retorna True se a probabilidade for >= 50%

def capturar_saldo(driver):
    imagem = capturar_tela(driver, 3, 1635, 130, 1775, 160)

    sharp = tratar_imagem(imagem)

    # Configurações adicionais para o Tesseract (modo PSM 6 e OCR específico para dígitos)
    custom_config = r'--oem 3 --psm 6 outputbase digits'

    # Executar OCR na imagem com a configuração customizada
    texto = pytesseract.image_to_string(sharp , config=custom_config)

    # Limpa e verifica se o texto extraído é um número válido com ponto decimal
    try:
        saldo = float(texto.strip())
        print("Saldo:", saldo)
        return saldo
    except ValueError:
        print("Falha ao extrair o número corretamente. Texto extraído:", texto)


def verificar_aposta(driver, resultado, num_apostas, valor_aposta, multiplicador, saldo_final, stop_win, stop_loss):
    if resultado == 's':
        if float(saldo_final) >= stop_win:
            print('META BATIDA!!! LEMBRE DE TUDO QUE JÁ PERDEU E CONTINUE AMANHÃ!\n')
            input("Pressione Enter para sair...")
            driver.quit()

        print("APOSTA GANHA!")
        
        # Se já tiver apostado e dado loss, reseta os valores de aposta e multiplicador
        if num_apostas > 1:
            valor_aposta = saldo_final * 0.02
            multiplicador = 1.5
            num_apostas = 0
    elif resultado == 'n':
        if float(saldo_final) <= stop_loss:
            print('LOSS BATIDO!!! LEMBRE DE TUDO QUE JÁ PERDEU E CONTINUE AMANHÃ!\n')
            input("Pressione Enter para sair...")
            driver.quit()

        print("APOSTA PERDIDA!")
        
        valor_aposta += valor_aposta / 2
        multiplicador += 0.5

    return num_apostas, valor_aposta, multiplicador

def preparar_aposta( valor_aposta, multiplicador):
    # Clica duplo no valor do auto saque
    pyautogui.doubleClick(1080, 990)
    # Digita o valor do multiplicador
    pyautogui.typewrite(str(multiplicador))
    time.sleep(0.5)
    # Clica duplo no valor da aposta
    pyautogui.doubleClick(714, 850)
    # Digita o valor da aposta
    pyautogui.typewrite(str(valor_aposta))
    time.sleep(0.5)

def apostar(num_aposta, valor_aposta, multiplicador):
    print("------------------------")
    print("Aposta nº", num_aposta)
    print("Valor:", valor_aposta)
    print("Multiplicador", multiplicador)
    print("------------------------")
    # Clica em 'APOSTA'
    pyautogui.click(1014, 870)
    time.sleep(0.5)
    # Clica em mostrar histórico
    pyautogui.click(1826, 333)
    time.sleep(0.5)
    # Clica no terminal
    pyautogui.click(2500, 392)
    time.sleep(0.5)
    print("CLique de apostar")

   

    
    
    
