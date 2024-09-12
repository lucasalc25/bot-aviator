import time
import pytesseract
import pyautogui
import cv2
import re
from PIL import Image
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
from tensorflow import keras
from keras import layers
from tensorflow.keras.layers import Dense
from keras import Sequential
from sklearn.preprocessing import MinMaxScaler


# Configurações do navegador
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
 
# Inicializa o navegador
servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico, options=chrome_options)

def capturar_tela(chave, x, y, xfinal, yfinal):
    # Aumenta o zoom em 50%
    driver.execute_script(f"document.body.style.zoom='{1.50}'")

    # Clica para mostrar o histórico
    pyautogui.click(1826, 333)

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

def imagem_pra_array(imagem):
    """Converte uma imagem PIL para um array numpy."""
    return np.array(imagem)

def comparar_imagens(img1, img2):
    """Compara duas imagens e retorna True se forem diferentes."""
    arr1 = imagem_pra_array(img1)
    arr2 = imagem_pra_array(img2)
    return not np.array_equal(arr1, arr2)

def corrigir_numero(item):
    # Remove qualquer ponto final na string
    if item.endswith('.'):
        item = item[:-1]
    
    # Se houver mais de um ponto, remove os pontos adicionais
    partes = item.split('.')
    if len(partes) > 2:
        # Junta as partes mantendo apenas um ponto decimal
        item = partes[0] + '.' + ''.join(partes[1:])
    
    return item

# Função para capturar os números
def capturar_numeros():
    imagem = capturar_tela(1, 590, 240, 1790, 325)

    sharp = tratar_imagem(imagem)

    # Configuração personalizada do Tesseract
    custom_config = r'--oem 3 --psm 6 outputbase digits'

    # Executar OCR na imagem com a configuração customizada
    text = pytesseract.image_to_string(sharp, config=custom_config)

    try:
        # Usa expressão regular para encontrar números com mais de 2 dígitos consecutivos
        # Separa a string em números com dois dígitos após o ponto decimal
        numeros = re.findall(r'\d{1,3}(?:\.\d{1,2})?', text)

        # Converte os números encontrados em ponto flutuante
        numeros_convertidos = []

        for numero in numeros:
            if '.' in numero:
                partes = numero.split('.')
                if len(partes[-1]) == 1:
                    numero = '.'.join(partes[:-1]) + '.' + partes[-1] + '0'  # Adiciona '0' se faltar um dígito
                elif len(partes[-1]) > 2:
                    numero = '.'.join(partes[:-1]) + '.' + partes[-1][:2]  # Mantém apenas 2 dígitos após o ponto
            else:
                numero += '.00'  # Adiciona '.00' se o número não tiver ponto decimal
            numeros_convertidos.append(float(numero))
        
        print("Números tratados: ",numeros_convertidos)
        return numeros_convertidos
     
    except ValueError as e:
        print("Erro ao converter string para float:", e)

def capturar_novo_numero():
    imagem = capturar_tela(2, 600, 195, 665, 225)

    sharp = tratar_imagem(imagem)

    # Configuração personalizada do Tesseract
    custom_config = r'--oem 3 --psm 6 outputbase digits'

    # Executar OCR na imagem com a configuração customizada
    text = pytesseract.image_to_string(sharp, config=custom_config)

    # Limpa e verifica se o texto extraído é um número válido com ponto decimal
    try:
        novo_numero = text.strip().replace('x', '').replace('%', '').replace('-', '')
        
        # Corrige números que podem estar incorretos
        if len(novo_numero.split('.')[0]) > 2:  # Verifica se o número parece grande demais
            novo_numero = novo_numero[:-2] + '.' + novo_numero[-2:]
            novo_numero = corrigir_numero(novo_numero)

        return float(novo_numero)
    except ValueError:
        print("Falha ao extrair o número corretamente. Texto extraído:", text)
        return None  # Retorne None em caso de falha

# Função para manter a lista de números atualizada
def atualizar_lista(lista, numero):
    lista.insert(0, numero)
    if len(lista) > 20:  # Mantém apenas os últimos 20 números
        lista.pop()
    return lista

def nova_lista(lista_numeros):
    novo_numero = capturar_novo_numero()

    if novo_numero is None:  # Verifica se novo_numero é None
        time.sleep(2)
        return

    if novo_numero != lista_numeros[0]:
        lista_numeros = atualizar_lista(lista_numeros, novo_numero)
        print(lista_numeros)
        
    return lista_numeros

# Função para preparar os dados
def preparar_dados(lista_numeros):
    if not lista_numeros:
        raise ValueError("A lista de números está vazia.")
    
    # Normaliza os números
    scaler = MinMaxScaler()
    numbers_normalized = scaler.fit_transform(np.array(lista_numeros).reshape(-1, 1))
    
    # Prepara os dados para o treinamento
    X, y = [], []
    for i in range(len(numbers_normalized) - 1):
        X.append(numbers_normalized[i])
        y.append(numbers_normalized[i + 1])
    return np.array(X), np.array(y)

def criar_modelo(input_shape):
    model = Sequential([
        Dense(64, input_shape=(input_shape,), activation='relu'),
        Dense(32, activation='relu'),
        Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Função para treinar a IA
def treinar_modelo(lista_numeros):
    if len(lista_numeros) < 20:
        raise ValueError("A lista de números deve ter pelo menos 20 elementos para o treinamento.")

    X, y = preparar_dados(lista_numeros)
    model = criar_modelo(X.shape[1])
    model.fit(X, y, epochs=10, batch_size=1, verbose=1)
    return model

# Faz previsões usando o modelo treinado
def fazer_previsao(model, last_number):
    scaler = MinMaxScaler()
    last_number_normalized = scaler.fit_transform(np.array([last_number]).reshape(-1, 1))
    prediction_normalized = model.predict(last_number_normalized)
    prediction = scaler.inverse_transform(prediction_normalized)
    return prediction[0][0]


# Acessa a página desejada
url = "https://www.claro.bet/slots/all/240/spribe/37591-806666-aviator?mode=fun"
driver.get(url)

# Aguarde a página carregar completamente
time.sleep(10)

lista_numeros = capturar_numeros()  # Captura os números

# Verificação da lista capturada
if not lista_numeros:
    print("Lista inicial não foi capturada.")
    driver.quit()

while True:
    if lista_numeros != nova_lista(lista_numeros):
        novo_numero = capturar_novo_numero()

        lista_numeros = atualizar_lista(lista_numeros, novo_numero)
    
        # Treina a IA
        modelo = treinar_modelo(lista_numeros)

        previsao = fazer_previsao(modelo, novo_numero)
        print(f"Previsão: {previsao}")

        if previsao >= 1.25:
            # Clica para ocultar o histórico
            pyautogui.click(1826, 333)

            driver.execute_script(f"document.body.style.zoom='{1.00}'")

            if lista_numeros != nova_lista(lista_numeros):

                resposta = input("O palpite estava correto? (s/n): ")
                
                if resposta.lower() == 's':
                    continue
                else:
                    for _ in range(3):
                        previsao = fazer_previsao(modelo, novo_numero + 1)
                        print(f"Tentativa adicional: {previsao}")
                        if previsao >= 1.25:
                            break
                    else:
                        print("Você bateu o stop.")
                        break
            else:
                continue
