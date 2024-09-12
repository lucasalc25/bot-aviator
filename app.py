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
from sklearn.ensemble import RandomForestClassifier
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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
        image.save("screenshot_saldo_cropped.png")
        # Carregar a imagem da tela capturada
        image = cv2.imread('screenshot_saldo_cropped.png')
    if chave == 3:
        image.save("screenshot_botao_cropped.png")
        # Carregar a imagem da tela capturada
        image = cv2.imread('screenshot_botao_cropped.png')
    if chave == 4:
        image.save("screenshot_mensagem_cropped.png")
        # Carregar a imagem da tela capturada
        image = cv2.imread('screenshot_mensagem_cropped.png')

    return image

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

def capturar_saldo():
    image = capturar_tela(2, 1635, 130, 1775, 160)

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
    print("Tipo de dado do saldo extraído:", type(text))
    print(text)

    # Limpa e verifica se o texto extraído é um número válido com ponto decimal
    try:
        saldo = float(text.strip())
        print("Tipo de dado do saldo convertido:",type(saldo))
        return saldo
    except ValueError:
        print("Falha ao extrair o número corretamente. Texto extraído:", text)

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


# Pré-processamento dos dados para treinar a IA
def preparar_dados(numeros):
    X = []
    y = []
    for i in range(len(numeros) - 1):
        X.append([numeros[i]])
        y.append(1 if numeros[i + 1] >= 1.25 else 0)
    return np.array(X), np.array(y)

def apostar(entrada, multiplicador):
    # Mostra opções automáticas
    pyautogui.click(972, 708)
    time.sleep(1)
    # Ativa auto saque
    pyautogui.click(999, 897)
    time.sleep(1)
    # Muda o valor de auto saque
    pyautogui.doubleClick(1092, 901)
    time.sleep(1)
    pyautogui.write(str(multiplicador))
    time.sleep(1)
    # Muda o valor de aposta
    pyautogui.doubleClick(720, 769)
    time.sleep(1)
    pyautogui.write(str(entrada))
    time.sleep(1)
    pyautogui.click(1011, 796)

def imagem_pra_array(image):
    """Converte uma imagem PIL para um array numpy."""
    return np.array(image)

def comparar_imagens(img1, img2):
    """Compara duas imagens e retorna True se forem diferentes."""
    arr1 = imagem_pra_array(img1)
    arr2 = imagem_pra_array(img2)
    return not np.array_equal(arr1, arr2)

def verificar_botao(x, y, xfinal, yfinal, intervalo=1):
    # Captura inicial da região do botão
    imagem_inicial_botao = capturar_tela(3, x, y, xfinal, yfinal)
    
    while True:
        time.sleep(intervalo)
        # Captura a imagem atual do botão
        imagem_atual_botao = capturar_tela(3, x, y, xfinal, yfinal)
        
        if comparar_imagens(imagem_inicial_botao, imagem_atual_botao):
            return True
        else:
            return False

def verificar_mensagem(x, y, xfinal, yfinal, intervalo=1):
     # Captura inicial da região da mensagem
    imagem_inicial_mensagem = capturar_tela(4, x, y, xfinal, yfinal)
    
    time.sleep(intervalo)
    # Captura a imagem atual da mensagem
    imagem_atual_mensagem = capturar_tela(4, x, y, xfinal, yfinal)
    
    if comparar_imagens(imagem_inicial_mensagem, imagem_atual_mensagem):
        print("Aposta ganha!")
        return True
    else:
        print("Aposta perdida!")
        return False

def verificar_resultado():
    """Verifica se o botão mudou e se a mensagem apareceu."""
    if verificar_botao(935, 700, 1110, 785) and verificar_mensagem(1036, 267, 1405, 332):
        return True
    else:
        return False 

def iniciar_apostas():
    tentativa = 1
    saldo = capturar_saldo()
    stop_win = saldo + saldo * 0.2
    stop_loss = saldo - saldo * 0.2

    while True:
        novo_saldo = capturar_saldo()

        if novo_saldo == stop_win:
            print("Meta diária atingida!")
            break
        if novo_saldo == stop_loss:
            print("Stop loss diário atingido!")
            break
        
        entrada = novo_saldo * 0.05
            
        if tentativa == 1:
            multiplicador = 1.25
            apostar(entrada, multiplicador)
        if tentativa == 2:
            multiplicador = 1.5
            apostar(entrada, multiplicador)
        if tentativa == 3:
            multiplicador = 2
            apostar(entrada, multiplicador)


        print("Aposta feita!")
        resultado = verificar_resultado()

        if resultado:
            print("Aposta ganha!")
        else:
            print("Aposta perdida!")
            tentativa += 1


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

accuracy = 0

# Loop até que a acurácia seja superior a 80%
while accuracy < 0.9:
    # Captura os números para treinar a IA
    numeros_capturados = capturar_numeros()

    saldo = capturar_saldo()
    print(saldo)

    if len(numeros_capturados) >= 19:  # Certifica-se de que há números suficientes para treinamento
        novos_X, novos_y = preparar_dados(numeros_capturados)

        # Concatena os novos dados aos dados já existentes
        if X.size > 0 and y.size > 0:
            X = np.vstack([X, novos_X])
            y = np.hstack([y, novos_y])
        else:
            X, y = novos_X, novos_y

        # Divide os dados em treinamento e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Treina a IA
        model.fit(X_train, y_train)

        # Avalia a IA
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Acurácia da IA: {accuracy * 100:.2f}%")

        # Se a acurácia for superior a 80%, começa a previsão em tempo real
        if accuracy >= 0.8:
            print("A IA atingiu a acurácia desejada! Iniciando as apostas...")
            iniciar_apostas()
        else:
            print("A IA ainda não atingiu a acurácia desejada. Aguardando para capturar novos dados...")
            time.sleep(360)  # Aguarda 10 minutos antes de capturar novos dados
    else:
        print("Números insuficientes para treinamento.")