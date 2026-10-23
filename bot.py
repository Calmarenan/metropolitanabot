import time
import requests
import os

# Link do stream da rádio
STREAM_URL = "https://play.wisestream.io/metropolitana985sp"

# Termos monitorados
PALAVRAS_CHAVE = [
    "senha",
    "apartamento",
    "senha do dia",
    "caçada ao apê"
]

# Suas credenciais do Telegram
TELEGRAM_BOT_TOKEN = "8693859276:AAHSg_fh0e6umW0Kx5u0n60YF3ygsVc6v4Q"
TELEGRAM_CHAT_ID = "7975917597"

def gravar_trecho_ao_vivo(duracao_segundos=20, nome_arquivo="bloco_atual.mp3"):
    """
    Grava um trecho do stream de áudio diretamente usando Python puro.
    Duração padrão configurada para 20 segundos.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://metropolitanafm.com.br/"
    }
    try:
        response = requests.get(STREAM_URL, headers=headers, stream=True, timeout=10)
        
        if response.status_code == 200:
            inicio = time.time()
            with open(nome_arquivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                    if time.time() - inicio > duracao_segundos:
                        break
            return True
    except Exception as e:
        print(f"Erro na conexão: {e}")
    
    return False

def verificar_palavra_chave(caminho_audio):
    """
    Lógica de transcrição (por enquanto simulada).
    Retorna True/False se encontrar a palavra.
    """
    return False, None

def enviar_para_telegram(caminho_audio, legenda):
    """
    Envia qualquer áudio gravado e uma legenda personalizada para o seu Telegram.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': legenda}
    
    try:
        with open(caminho_audio, 'rb') as audio:
            files = {'audio': audio}
            requests.post(url, data=payload, files=files)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

def iniciar_monitoramento():
    print("🤖 Robô conectado e a gravar blocos de 20 segundos da Metropolitana FM!")
    
    # Guarda o momento em que o robô começou a rodar
    ultimo_envio_status = time.time()
    
    # 6 horas em segundos (6 * 60 * 60 = 21600 segundos)
    # Dica: se quiser testar o envio já, troque temporariamente para 30 segundos!
    INTERVALO_STATUS = 6 * 60 * 60  
    
    while True:
        arquivo_temp = "bloco_atual.mp3"
        
        # Tenta gravar um bloco de 20 segundos
        sucesso = gravar_trecho_ao_vivo(duracao_segundos=20, nome_arquivo=arquivo_temp)
        
        if sucesso and os.path.exists(arquivo_temp) and os.path.getsize(arquivo_temp) > 0:
            print("✅ Bloco de 20 segundos gravado com sucesso! Analisando...")
            
            # 1. Verifica se encontrou alguma palavra-chave da promoção
            detectado, palavra = verificar_palavra_chave(arquivo_temp)
            if detectado:
                print(f"🔥 Encontrado termo: {palavra}!")
                enviar_para_telegram(arquivo_temp, f"🚨 Palavra-chave detectada: {palavra}")
            
            # 2. Verifica se já passaram 6 horas desde o último envio de status
            tempo_atual = time.time()
            if tempo_atual - ultimo_envio_status >= INTERVALO_STATUS:
                print("⏰ A enviar o relatório de funcionamento de 6 em 6 horas...")
                enviar_para_telegram(
                    arquivo_temp, 
                    "🟢 Robô ativo! O monitoramento de blocos de 20s está a funcionar perfeitamente."
                )
                ultimo_envio_status = tempo_atual  # Reinicia a contagem das 6 horas
            
            if os.path.exists(arquivo_temp):
                os.remove(arquivo_temp)
        else:
            print("⚠️ A aguardar stream... Tentando novamente em 3 segundos.")
            time.sleep(3)

if __name__ == "__main__":
    iniciar_monitoramento()
