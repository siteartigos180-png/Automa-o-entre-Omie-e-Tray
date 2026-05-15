import requests
import os

token = os.getenv('ACCESS_TOKEN_TRAY')
url_loja = "https://www.tray.com.br/api/products"

def testar_tray():
    print("Iniciando teste de conexão com a Tray...")
    resposta = requests.get(f"{url_loja}?access_token={token}")
    
    if resposta.status_code == 200:
        print("✅ Sucesso! O GitHub conseguiu acessar sua loja Tray.")
    else:
        print(f"❌ Erro na conexão. Código: {resposta.status_code}")
        print("Verifique se o Token está correto nos Secrets.")

if __name__ == "__main__":
    testar_tray()
