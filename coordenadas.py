def processar_string(input_string):
    # Lista para armazenar os números processados
    numeros_processados = []
    
    # Remove espaços extras e separa os números por pontos
    input_string = input_string.replace(" ", "")
    partes = input_string.split('.')
    
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

# Exemplo de uso
input_string = "6.331.131.381.184.011.6020.203.032.752.315.611.413.512.353.631.19 48.621.345.721.341.001.441.541.283.702.16"
numeros = processar_string(input_string)
print(numeros)
