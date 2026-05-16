import requests
import os

def renovar_token():
    print("🔄 Access Token vencido. Tentando renovar com o Refresh Token...")
    url = "https://391250.commercesuite.com.br/web_api/auth"
    payload = {
        "refresh_token": os.getenv('REFRESH_TOKEN_TRAY').strip()
    }
    resposta = requests.get(url, params=payload) # Na Tray, renovação usa GET com query params
    
    if resposta.status_code == 200 or resposta.status_code == 201:
        dados = resposta.json()
        novo_access = dados.get('access_token')
        print(f"✅ Token renovado com sucesso!")
        print(f"ATENÇÃO: Guarde esse novo Access Token se quiser: {novo_access}")
        return novo_access
    else:
        print(f"❌ Erro ao renovar o token: {resposta.status_code}")
        print(resposta.text)
        return None

def listar_produtos():
    token = os.getenv('ACCESS_TOKEN_TRAY')
    url = "https://391250.commercesuite.com.br/web_api/products"
    
    print("Consultando a lista de produtos na Tray...")
    resposta = requests.get(url, params={'access_token': token})
    
    # Se der erro de não autorizado (vencido), tenta renovar na hora
    if resposta.status_code == 401:
        novo_token = renovar_token()
        if novo_token:
            print("Retentando consulta com o novo token...")
            resposta = requests.get(url, params={'access_token': novo_token})

    if resposta.status_code == 200:
        dados = resposta.json()
        produtos = dados.get('Products', [])
        print(f"✅ Sucesso! Encontramos {len(produtos)} produtos nesta página.")
        print("-" * 30)
        for p in produtos:
            prod = p.get('Product')
            print(f"ID: {prod.get('id')} | Nome: {prod.get('name')} | Estoque: {prod.get('stock')}")
    else:
        print(f"❌ Erro final ao listar: {resposta.status_code}")
        print(resposta.text)

if __name__ == "__main__":
    listar_produtos()
