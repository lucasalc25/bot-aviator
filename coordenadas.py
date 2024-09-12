import pyautogui
from pynput import mouse

# Função chamada quando o mouse é clicado
def on_click(x, y, button, pressed):
    if pressed:
        # Mostra as coordenadas na tela
        print(f"Mouse clicked at ({x}, {y})")

        # Para a escuta do mouse após o primeiro clique
        return False

# Inicia a escuta do mouse
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
