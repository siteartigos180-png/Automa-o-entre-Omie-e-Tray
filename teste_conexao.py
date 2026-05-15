import requests
import os

def gerar_token():
    url = "https://391250.commercesuite.com.br/web_api/auth"
    
    # Pegando os dados do seu "cofre" no GitHub
    payload = {
        "consumer_key": os.getenv('CONSUMER_KEY').strip(),
        "consumer_secret": os.getenv('CONSUMER_SECRET').strip(),
        "code": os.getenv('CODE_TRAY').strip()
    }
    
    print(f"Tentando conexão com a loja 391250...")
    # O segredo pode estar aqui: enviando exatamente como a Tray pede
    resposta = requests.post(url, data=payload)
    
    print(f"Resposta da Tray: {resposta.status_code}")
    print(resposta.text)

if __name__ == "__main__":
    gerar_token()
