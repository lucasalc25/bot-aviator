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

def imagem_pra_array(imagem):
    """Converte uma imagem PIL para um array numpy."""
    return np.array(imagem)

def comparar_imagens(img1, img2):
    """Compara duas imagens e retorna True se forem diferentes."""
    arr1 = imagem_pra_array(img1)
    arr2 = imagem_pra_array(img2)
    return not np.array_equal(arr1, arr2)

def corrigir_e_validar_numero(item):
    # Remover possíveis erros de pontuação
    item = item.strip().replace(',', '.')

    # Se houver mais de um ponto, manter apenas um
    partes = item.split('.')
    if len(partes) > 2:
        # Reunir a parte inteira e a parte decimal
        item = f"{partes[0]}.{''.join(partes[1:])}"
    
    # Certificar que o número seja válido e >= 1.00
    try:
        numero = float(item)
        if numero >= 1.00:
            return numero
    except ValueError:
        pass

    return None

# Função para capturar os números
def capturar_numeros():
    imagem = capturar_tela(1, 590, 240, 1790, 325)

    sharp = tratar_imagem(imagem)

    # Configuração personalizada do Tesseract
    custom_config = r'--oem 3 --psm 6 outputbase digits'

    # Executar OCR na imagem com a configuração customizada
    texto = pytesseract.image_to_string(sharp, config=custom_config)
    print(texto)

    try:
         # Lista para armazenar os números processados
        numeros_processados = []

        texto = texto.replace(" ", "").replace("x", "").replace("\n", "")
        print(texto)
        partes = texto.split('.')
        print(partes)
        
        # Itera pelas partes, combinando-as para formar números válidos
        i = 0
        while i < len(partes) - 1:
            # Verifica a parte inteira
            parte_inteira = partes[i]
            parte_decimal = partes[i + 1][:2]  # Pega os dois primeiros dígitos após o ponto
            
            if i > 0:
                # Remove os dois primeiros dígitos da parte inteira, a partir do segundo número
                parte_inteira = parte_inteira[2:]

            # Cria o número formatado com dois dígitos após o ponto decimal
            numero_formatado = f"{parte_inteira}.{parte_decimal}"
            numeros_processados.append(f"{float(numero_formatado):.2f}")
            
            # Avança para a próxima parte
            i += 1
        
        return numeros_processados
     
    except ValueError as e:
        print("Erro ao converter string para float:", e)

def capturar_novo_numero():
    imagem = capturar_tela(2, 600, 195, 670, 225)

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
            novo_numero = corrigir_e_validar_numero(novo_numero)

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

# Acessa a página desejada
url = "https://www.claro.bet/slots/all/240/spribe/37591-806666-aviator?mode=fun"
driver.get(url)

# Aguarde a página carregar completamente
time.sleep(10)

# Aumenta o zoom em 50%
driver.execute_script(f"document.body.style.zoom='{1.50}'")

# Clica para mostrar o histórico
pyautogui.click(1826, 333)

lista_numeros = capturar_numeros()  # Captura os números

# Clica para mostrar o histórico
pyautogui.click(1826, 333)


# Simulação contínua de geração de números e previsão
while True:
    novo_numero = capturar_novo_numero()

    if novo_numero and novo_numero != lista_numeros[0]:
        # Adiciona uma pequena pausa
        time.sleep(2)
        lista_numeros = atualizar_lista(lista_numeros, novo_numero)
        print(lista_numeros)


    