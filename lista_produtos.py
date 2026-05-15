import requests
import os

def listar_produtos():
    # Usamos o Access Token que você acabou de gerar
    token = os.getenv('ACCESS_TOKEN_TRAY')
    url = "https://391250.commercesuite.com.br/web_api/products"
    
    params = {'access_token': token}
    
    print("Consultando a lista de produtos na Tray...")
    resposta = requests.get(url, params=params)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        produtos = dados.get('Products', [])
        
        print(f"✅ Sucesso! Encontramos {len(produtos)} produtos nesta página.")
        print("-" * 30)
        
        for p in produtos:
            prod = p.get('Product')
            print(f"ID: {prod.get('id')} | Nome: {prod.get('name')} | Estoque: {prod.get('stock')}")
            
    else:
        print(f"❌ Erro ao listar: {resposta.status_code}")
        print(resposta.text)

if __name__ == "__main__":
    listar_produtos()
