import os
import requests

def gerar_novo_token():
    # URL de autenticação confirmada
    url = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/auth"
    
    # Puxando as credenciais das variáveis de ambiente do GitHub
    consumer_key = os.environ.get("CONSUMER_KEY_TRAY")
    consumer_secret = os.environ.get("CONSUMER_SECRET_TRAY")
    codigo_instalacao = "efcd9cb9fa9715c2f86f634847192d157571e6b3546ddb0d60abca1390f83140"
    
    # Montando o payload com os 3 campos obrigatórios que a Tray exigiu
    payload = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "code": codigo_instalacao
    }
    
    print("🔑 Enviando chaves e código para gerar o novo Access Token...")
    response = requests.post(url, data=payload)
    
    if response.status_code in [200, 201]:
        dados = response.json()
        novo_token = dados.get("access_token")
        print("\n" + "="*50)
        print(f"✅ NOVO ACCESS TOKEN GERADO COM SUCESSO!")
        print(f"👉 COPIE ESTE TEXTO ABAIXO:")
        print(f"\n{novo_token}\n")
        print("="*50)
    else:
        print(f"❌ Erro ao gerar token: {response.status_code} - {response.text}")

if __name__ == "__main__":
    gerar_novo_token()
