import random
import time
import pytesseract
import pyautogui
from PIL import Image
import cv2
import numpy as np
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from sklearn.linear_model import LogisticRegression

# Configurações do navegador
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
 
# Inicializa o navegador
servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico, options=chrome_options)

# Realiza o login, se necessário
def login(username, password):
    try:
        wait = WebDriverWait(driver, 10)
        user_field = driver.find_element('xpath', '//*[@id="username"]')
        pass_field = driver.find_element('xpath', '//*[@id="password"]')
        user_field.send_keys(username)
        pass_field.send_keys(password)
        pass_field.send_keys(Keys.RETURN)
    except Exception as e:
        print("Login não necessário ou falhou:", e)

def capturar_tela(chave, x, y, xfinal, yfinal):
     # Captura a tela e salva como imagem
    screenshot_path = "screenshot.png"
    driver.save_screenshot(screenshot_path)

    # Use o Tesseract para extrair texto da imagem
    # Certifique-se de que o Tesseract esteja instalado e configurado no PATH do sistema
    # Para Windows, configure o caminho abaixo se necessário:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Abre a imagem completa
    image = Image.open(screenshot_path)
    
    # Recorta e salva a imagem para a área especificada
    image = image.crop((x, y, xfinal, yfinal))

    if chave == 1:
        image.save("screenshot_multis_cropped.png")
        # Carregar a imagem da tela capturada
        image = cv2.imread('screenshot_multis_cropped.png')
    if chave == 2:
        image.save("screenshot_novo_num_cropped.png")
        # Carregar a imagem da tela capturada
        image = cv2.imread('screenshot_novo_num_cropped.png')
    if chave == 3:
        image.save("screenshot_saldo_cropped.png")
        # Carregar a imagem da tela capturada
        image = cv2.imread('screenshot_saldo_cropped.png')
    if chave == 4:
        image.save("screenshot_botao_cropped.png")
        # Carregar a imagem da tela capturada
        image = cv2.imread('screenshot_botao_cropped.png')
    if chave == 5:
        image.save("screenshot_mensagem_cropped.png")
        # Carregar a imagem da tela capturada
        image = cv2.imread('screenshot_mensagem_cropped.png')

    return image

def imagem_pra_array(image):
    """Converte uma imagem PIL para um array numpy."""
    return np.array(image)

def comparar_imagens(img1, img2):
    """Compara duas imagens e retorna True se forem diferentes."""
    arr1 = imagem_pra_array(img1)
    arr2 = imagem_pra_array(img2)
    return not np.array_equal(arr1, arr2)

def verificar_numero(x, y, xfinal, yfinal, intervalo=1):
    # Captura inicial da região do botão
    imagem_inicial_numero = capturar_tela(2, x, y, xfinal, yfinal)
    
    while True:
        time.sleep(intervalo)
        # Captura a imagem atual do botão
        imagem_atual_numero = capturar_tela(2, x, y, xfinal, yfinal)
        
        if comparar_imagens(imagem_inicial_numero, imagem_atual_numero):
            return True
        else:
            return False

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
    image = capturar_tela(1, 780, 240, 1850, 325)

    # Convert para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aumenta o contraste
    gray = cv2.convertScaleAbs(gray, alpha=2.5, beta=0)

    # Aplicar um filtro de nitidez para melhorar a definição dos números
    kernel = np.array([[0, -1, 0],
                    [-1,  5,-1],
                    [0, -1, 0]])
    sharp = cv2.filter2D(gray, -1, kernel)

    # Configuração personalizada do Tesseract
    custom_config = r'--oem 3 --psm 6 outputbase digits'

    # Executar OCR na imagem com a configuração customizada
    text = pytesseract.image_to_string(sharp, config=custom_config)

    try:
        # Pós-processamento
        numeros = []
        for item in text.split():
            # Remove 'x' e '%' e verifica o formato esperado
            item = item.replace('x', '').replace('%', '')
            if item.replace('.', '', 1).isdigit():
                # Corrige números que podem estar incorretos
                if len(item.split('.')[0]) > 2:  # Verifica se o número parece grande demais
                    item = item[:-2] + '.' + item[-2:]
                    item = corrigir_numero(item)
                numeros.append(float(item))

        print("Números extraídos:", numeros)
        return numeros
     
    except ValueError as e:
        print("Erro ao converter string para float:", e)

def capturar_novo_numero():
    image = capturar_tela(2, 600, 250, 680, 280)

    # Convert para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aumenta o contraste
    gray = cv2.convertScaleAbs(gray, alpha=2.5, beta=0)

    # Aplicar um filtro de nitidez para melhorar a definição dos números
    kernel = np.array([[0, -1, 0],
                    [-1,  5,-1],
                    [0, -1, 0]])
    sharp = cv2.filter2D(gray, -1, kernel)

    # Configuração personalizada do Tesseract
    custom_config = r'--oem 3 --psm 6 outputbase digits'

    # Executar OCR na imagem com a configuração customizada
    text = pytesseract.image_to_string(sharp, config=custom_config)

    # Limpa e verifica se o texto extraído é um número válido com ponto decimal
    try:
        novo_numero = float(text.strip())

        # Converte números negativos em positivos
        if novo_numero < 0:
            novo_numero = abs(novo_numero)

        return novo_numero
    except ValueError:
        print("Falha ao extrair o número corretamente. Texto extraído:", text)
        return None  # Retorne None em caso de falha

def capturar_saldo():
    image = capturar_tela(3, 1635, 130, 1775, 160)

    # Convert para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aumenta o contraste
    gray = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)

    # Aplica um filtro de nitidez
    kernel = np.array([[0, -1, 0],
                    [-1,  5,-1],
                    [0, -1, 0]])
    sharp  = cv2.filter2D(gray, -1, kernel)

    # Configurações adicionais para o Tesseract (modo PSM 6 e OCR específico para dígitos)
    custom_config = r'--oem 3 --psm 6 outputbase digits'

    # Executar OCR na imagem com a configuração customizada
    text = pytesseract.image_to_string(sharp , config=custom_config)

    # Limpa e verifica se o texto extraído é um número válido com ponto decimal
    try:
        saldo = float(text.strip())
        print("Saldo: R$", saldo)
        return saldo
    except ValueError:
        print("Falha ao extrair o número corretamente. Texto extraído:", text)


# Função para manter a lista de números atualizada
def atualizar_lista(lista, numero):
    lista.insert(0, numero)
    if len(lista) > 20:
        lista.pop()
    return lista

# Função para prever o próximo número usando IA com base nos 20 números mais recentes
def prever_proximo_numero(ia_model, lista):
    previsao = ia_model.predict_proba([lista])[0][1]  # Probabilidade de ser maior que 1.25
    if previsao >= 0.8:
        print("Alerta: Alta probabilidade do próximo número ser maior que 1.25")
    return previsao

# Acessa a página desejada
url = "https://www.claro.bet/slots/all/240/spribe/37591-806666-aviator?mode=fun"  # Substitua pela URL real
driver.get(url)

# Aumenta o zoom em 50%
zoom_level = 1.50   
driver.execute_script(f"document.body.style.zoom='{zoom_level}'") # permite executar qualquer código JavaScript dentro da página carregada

# Substitua 'usuario' e 'senha' pelos valores reais
#login('lucas.alc25@gmail.com', '!Alcantara32383910')

# Aguarde a página carregar completamente
time.sleep(10)

# Clica para mostrar o histórico
pyautogui.click(1826, 333)

# Inicializando a lista com 20 números aleatórios
lista_numeros = capturar_numeros()

# Buffer para armazenar conjuntos de treinamento variados
training_buffer = []

ia_model = None  # Inicializando a variável ia_model como None

# Simulação contínua de geração de números e previsão
while True:
    novo_numero = capturar_novo_numero()

    if novo_numero is None:  # Verifica se novo_numero é None
        time.sleep(1)
        continue

    if novo_numero != lista_numeros[0]:
        lista_numeros = atualizar_lista(lista_numeros, novo_numero)
        print(lista_numeros)
        
        # Verificar a classe do último número e adicionar ao buffer
        y_classificacao = 1 if float(novo_numero) > 1.25 else 0
        training_buffer.append((lista_numeros[:], y_classificacao))
        
        # Verificar se o buffer tem exemplos de ambas as classes
        classes_no_buffer = [y for _, y in training_buffer]
        if len(set(classes_no_buffer)) > 1:
            x_train = np.array([x for x, _ in training_buffer])
            y_train = np.array(classes_no_buffer)
            ia_model = LogisticRegression()
            ia_model.fit(x_train, y_train)
        
        # Verificar se o modelo foi treinado antes de fazer a previsão
        if ia_model:
            previsao = prever_proximo_numero(ia_model, lista_numeros)

    
    time.sleep(1)
    