import requests
import os

# Dados que você guardou nos Secrets
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
code = os.getenv('CODE_TRAY')
url_base = "https://391250.commercesuite.com.br/web_api/auth"

def gerar_token():
    print("Tentando gerar o Access Token oficial...")
    payload = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "code": code
    }
    
    resposta = requests.post(url_base, data=payload)
    
    if resposta.status_code == 201 or resposta.status_code == 200:
        dados = resposta.json()
        print("✅ SUCESSO! Token gerado.")
        print(f"Seu novo Access Token é: {dados.get('access_token')}")
    else:
        print(f"❌ Erro: {resposta.status_code}")
        print(resposta.text)

if __name__ == "__main__":
    gerar_token()
