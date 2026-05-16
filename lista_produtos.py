import requests
import os

def listar_produtos():
    # Usando o Access Token ativo
    token = os.getenv('ACCESS_TOKEN_TRAY').strip()
    url = "https://391250.commercesuite.com.br/web_api/products"
    
    print("📦 Consultando a lista de produtos cadastrados na Tray de testes...")
    resposta = requests.get(url, params={'access_token': token})
    
    if resposta.status_code == 200:
        dados = response_json = resposta.json()
        produtos = dados.get('Products', [])
        print(f"🎉 SUCESSO! Encontramos {len(produtos)} produtos cadastrados:")
        print("-" * 50)
        for p in produtos:
            prod = p.get('Product')
            print(f"ID: {prod.get('id')} | Nome: {prod.get('name')} | Estoque: {prod.get('stock')}")
    else:
        print(f"❌ Erro ao listar produtos: {resposta.status_code}")
        print(resposta.text)

if __name__ == "__main__":
    listar_produtos()
